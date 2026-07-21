'''
Text rendering using Freetype for proper OpenGL glyph rendering with rotation support.

Copyright (C) 2025 Jakub Kamyk

This file is part of DAEDALUS.

DAEDALUS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

DAEDALUS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DAEDALUS.  If not, see <http://www.gnu.org/licenses/>.
'''

import numpy as np
from OpenGL.GL import *
# from freetype import FT_Load_Glyph, FT_LOAD_RENDER, FT_Init_FreeType, FT_New_Face
from PIL import Image, ImageDraw, ImageFont
import os


class FreetypeTextRenderer:
    """Renders text using Freetype with support for rotation in OpenGL."""
    
    def __init__(self, font_size=8, font_path=None):
        """
        Initialize the text renderer.
        
        Args:
            font_size: Size of the font in pixels
            font_path: Path to TTF font file. If None, uses system default.
        """
        self.font_size = font_size
        self.texture_cache = {}  # Cache textures for rendered text
        self.font_path = font_path or self._get_default_font()
        
    def _get_default_font(self):
        """Get path to a default system font."""
        # Try common Windows font locations
        possible_paths = [
            "C:\\Windows\\Fonts\\Arial.ttf",
            "C:\\Windows\\Fonts\\Helvetica.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Fallback to a very basic font rendering without specific font file
        return None
    
    def _render_text_to_image(self, text, color=(255, 255, 255)):
        """
        Render text to a PIL image.
        
        Args:
            text: Text string to render
            color: RGB tuple (0-255)
        
        Returns:
            PIL Image object with rendered text
        """
        if self.font_path and os.path.exists(self.font_path):
            try:
                font = ImageFont.truetype(self.font_path, self.font_size)
            except:
                font = ImageFont.load_default()
        else:
            font = ImageFont.load_default()
        
        # Create a temporary image to measure text
        temp_img = Image.new('RGBA', (1, 1), color=(0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        # bbox = temp_draw.textbbox((0, 0), text, font=font)
        # text_width = bbox[2] - bbox[0]
        # text_height = bbox[3] - bbox[1]
        
        # # Add padding
        # padding = max(4, self.font_size // 6)
        # width = text_width + padding * 2
        # height = text_height + padding * 2

        ascent, descent = font.getmetrics()

        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        text_height = ascent + descent
        padding = max(2, self.font_size // 6)

        width  = text_width + 2 * padding
        height = text_height + 2 * padding
        
        # Create the actual image
        img = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw text
        draw.text((padding, padding), text, font=font, fill=(*color, 255))
        
        return img
    
    def _image_to_texture(self, image):
        """
        Convert a PIL image to an OpenGL texture.
        
        Args:
            image: PIL Image object
        
        Returns:
            OpenGL texture ID
        """
        # Flip image vertically because PIL and OpenGL have different Y-axis conventions
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        
        # Convert image to proper format
        img_data = image.tobytes('raw', 'RGBA', 0, -1)
        
        # Create texture
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        
        # Set pixel unpacking to match PIL's layout
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 
                     0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        
        return texture, image.width, image.height
    
    def render_text_screen_space(self, text, x, y, angle=0, color=(255, 255, 255), centered=False, viewport_height=None):
        """
        Render text in screen/pixel space (for rulers and overlays).
        
        Args:
            text: Text string to render
            x: X coordinate in screen/pixel space
            y: Y coordinate in screen/pixel space  
            angle: Rotation angle in degrees
            color: RGB tuple (0-255)
            centered: If True, center text at (x, y)
            viewport_height: Height of viewport in pixels (for Y-flip)
        """
        # Convert color to tuple if it's a list
        color = tuple(color) if isinstance(color, (list, tuple)) else color
        
        # Check cache
        cache_key = (text, color, self.font_size)
        if cache_key not in self.texture_cache:
            img = self._render_text_to_image(text, color)
            texture, width, height = self._image_to_texture(img)
            self.texture_cache[cache_key] = (texture, width, height)
        else:
            texture, width, height = self.texture_cache[cache_key]
        
        # Save projection and modelview matrices
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        
        if viewport_height is None:
            viewport_height = glGetIntegerv(GL_VIEWPORT)[3]
        
        # Set up screen-space projection (pixel coords)
        viewport = glGetIntegerv(GL_VIEWPORT)
        glOrtho(0, viewport[2], viewport[3], 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Translate to screen position
        glTranslatef(x, y, 0)
        
        # Rotate around screen space
        glRotatef(angle, 0, 0, 1)
        
        # Center if requested
        offset_x = -width / 2 if centered else 0
        offset_y = -height / 2 if centered else 0
        
        # Draw quad with texture in screen space (no scaling needed)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor4f(1, 1, 1, 1)
        
        glBegin(GL_QUADS)
        # Texture coordinates for flipped image
        glTexCoord2f(0, 0); glVertex2f(offset_x, offset_y)
        glTexCoord2f(1, 0); glVertex2f(offset_x + width, offset_y)
        glTexCoord2f(1, 1); glVertex2f(offset_x + width, offset_y + height)
        glTexCoord2f(0, 1); glVertex2f(offset_x, offset_y + height)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        
        # Restore matrices
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        glDisable(GL_BLEND)

    def get_text_size(self, text):
        """Return cached (width, height) in pixels for rendered text (creates texture if needed)."""
        # Use default color and font_size for cache key
        cache_key = (text, (255, 255, 255), self.font_size)
        if cache_key not in self.texture_cache:
            img = self._render_text_to_image(text)
            texture, width, height = self._image_to_texture(img)
            self.texture_cache[cache_key] = (texture, width, height)
        else:
            _, width, height = self.texture_cache[cache_key]
        return width, height
    
    def render_text(self, text, x, y, angle=0, color=(255, 255, 255), centered=False):
        """
        Render text at specified position with optional rotation.
        
        Args:
            text: Text string to render
            x: X coordinate in world space
            y: X coordinate in world space
            angle: Rotation angle in degrees (0-360)
            color: RGB tuple (0-255)
            centered: If True, center text at (x, y)
        """
        # Convert color to tuple if it's a list (for hashability in cache)
        color = tuple(color) if isinstance(color, (list, tuple)) else color
        
        # Check cache
        cache_key = (text, color, self.font_size)
        if cache_key not in self.texture_cache:
            img = self._render_text_to_image(text, color)
            texture, width, height = self._image_to_texture(img)
            self.texture_cache[cache_key] = (texture, width, height)
        else:
            texture, width, height = self.texture_cache[cache_key]
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Save matrix state
        glPushMatrix()
        
        # Translate to position
        glTranslatef(x, y, 0)
        
        # Rotate
        glRotatef(angle, 0, 0, 1)
        
        # Center if requested
        offset_x = -width / 2 if centered else 0
        offset_y = -height / 2 if centered else 0
        
        # Draw quad with texture
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor4f(1, 1, 1, 1)  # White to preserve texture colors
        
        # Scale from pixel space to world space
        # Adjust these scale factors if text appears too big/small
        scale_x = 1
        scale_y = 1 # 0.003
        
        glBegin(GL_QUADS)
        # Texture coordinates for flipped image
        glTexCoord2f(0, 0); glVertex2f(offset_x * scale_x, offset_y * scale_y)
        glTexCoord2f(1, 0); glVertex2f((offset_x + width) * scale_x, offset_y * scale_y)
        glTexCoord2f(1, 1); glVertex2f((offset_x + width) * scale_x, (offset_y + height) * scale_y)
        glTexCoord2f(0, 1); glVertex2f(offset_x * scale_x, (offset_y + height) * scale_y)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        glDisable(GL_BLEND)
    
    def clear_cache(self):
        """Clear the texture cache."""
        for texture, _, _ in self.texture_cache.values():
            glDeleteTextures([texture])
        self.texture_cache.clear()
    
    def __del__(self):
        """Clean up textures when renderer is destroyed."""
        self.clear_cache()

def draw_text(target, text, x, y, angle=0, centered=False):
    """
    Render text in screen-space using a viewport or render-context-like object.

    Args:
        target: An object exposing text_renderer, text_color, and height.
        text: Text string to render.
        x: X coordinate in screen/pixel space.
        y: Y coordinate in screen/pixel space.
        angle: Rotation angle in degrees.
        centered: If True, center text at (x, y).
    """
    text = str(text)
    renderer = getattr(target, "text_renderer", None)
    if renderer is None:
        return

    color = getattr(target, "text_color", (255, 255, 255))
    height = getattr(target, "height", None)
    if callable(height):
        height = height()

    renderer.render_text_screen_space(
        text,
        x,
        y,
        angle=angle,
        color=color,
        centered=centered,
        viewport_height=height,
    )