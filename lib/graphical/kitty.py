from math import floor
import ustruct

class Color:
    @classmethod
    def rgb(self, r, g, b):
        """Return 24-bit color value.

        Args:
            r (int): Red value (0-255).
            g (int): Green value (0-255).
            b (int): Blue value (0-255).
        """
        
        return (r << 16) | (g << 8) | b

    @classmethod
    def hex(self, hex_color):
        """Return 24-bit color value.

        Args:
            hex_color (string): Hex color representation.
        """
        
        hex_color = hex_color.lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        return self.rgb(r, g, b)

class Font:
    bit_pos = {1: 0, 2: 1, 4: 2, 8: 3, 16: 4, 32: 5, 64: 6, 128: 7, 256: 8}
    
    def __init__(self, path, width, height, start_letter = 32, letter_count = 96):
        """Load X-GLCD font data from text file.

        Args:
            path (string): Full path of font file.
        """
        
        self.width = width
        self.height = height
        self.start_letter = start_letter
        self.letter_count = letter_count
        self.bytes_per_letter = self.load_font(path)
        self.font_path = path
    
    def load_font(self, path):
        length = 0
        
        with open(path, 'r') as f:
            for line in f:
                length = len(bytearray(line, 'utf-8'))
                break
        
        return length
    
    @micropython.native
    def letters(self, letter):
        letter_index = ord(letter) - self.start_letter
        offset = self.bytes_per_letter * letter_index
        
        with open(self.font_path, 'rb') as f:
            f.seek(offset)
            line = f.read(self.bytes_per_letter - 1)
            line = line.decode('utf8')
            letter_bytes = bytearray(int(b, 16) for b in line.split(','))
            f.close()
            
        return letter_bytes
    
    def lit_bits(self, n):
        """Return positions of 1 bits only."""
        
        while n:
            b = n & (~n+1)
            yield self.bit_pos[b]
            n ^= b
    
    @micropython.native
    def get_width_height(self, letter):
        """Return width and height of letter."""
        
        # Get index of letter
        letter_ord = ord(letter) - self.start_letter
        
        # Confirm font contains letter
        if letter_ord >= self.letter_count:
            print('Font does not contain character: ' + letter)
            return 0, 0
        
        return self.letters(letter)[0], self.height
    
    @micropython.native
    def get_letter(self, letter, landscape=False):
        """Convert letter byte data to X,Y pixels for transparent drawing.

        Args:
            letter (string): Letter to return (must exist within font).
            landscape (bool): Orientation (default: False = portrait)
        Yields:
            (int, int): X,Y relative position of bits to draw
        """
        
        # Get index of letter
        letter_ord = ord(letter) - self.start_letter
        
        # Confirm font contains letter
        if letter_ord >= self.letter_count:
            print('Font does not contain character: ' + letter)
            return b'', 0, 0

        # Get width of letter (specified by first byte)
        letter_height = self.height
        x = 0

        # Determine number of bytes per letter Y column
        byte_height = int(letter_height / 8) + (letter_height % 8 > 0)
        bh = 0
        
        # Loop through letter byte data and convert to pixel data
        for b in self.letters(letter)[1:]:
            # Process only colored bits
            for bit in self.lit_bits(b):
                if landscape:
                    yield letter_height - ((bh << 3) + bit), x
                else:
                    yield x, (bh << 3) + bit
            
            if bh < byte_height - 1:
                # Next column byte
                bh += 1
            else:
                # Next column
                x += 1
                bh = 0
    
    @micropython.native
    def get_text_width_height(self, text):
        total_height = 0
        total_width = 0

        for letter in text:
            width, total_height = self.get_width_height(letter)
            total_width += width
        
        return total_width, total_height
    
class Kitty():
    def __init__(self, gpu):
        self.gpu = gpu
    
    def reverse(self, byte_arr):
        @micropython.asm_thumb
        def reverse_asm(r0, r1):
            add(r4, r0, r1)
            sub(r4, 1)
            label(LOOP)
            ldrb(r5, [r0, 0])
            ldrb(r6, [r4, 0])
            strb(r6, [r0, 0])
            strb(r5, [r4, 0])
            add(r0, 1)
            sub(r4, 1)
            cmp(r4, r0)
            bpl(LOOP)
            
        reverse_asm(byte_arr, len(byte_arr))
    
    @micropython.native
    def set_buffer_pix(self, x, y, w, b, color):
        offset = ((y * w) + x) * 3
        b[offset:offset + 3] = color.to_bytes(3, 'big')
        return b
    
    @micropython.native
    def draw_circle(self, x0, y0, r, color):
        diam = (r * 2)
        arr_size = (diam + 1) * (diam + 1)
        buffer = bytearray(arr_size * 3)
        
        def set_buffer_pix(xp, yp, color):
            offset = ((yp * (diam + 1)) + xp) * 3
            buffer[offset:offset + 3] = color.to_bytes(3, 'big')
        
        f = 1 - r
        dx = 1
        dy = -r - r
        x = 0
        y = r
        
        set_buffer_pix(r, diam, color)
        set_buffer_pix(r, 0, color)
        set_buffer_pix(diam, r, color)
        set_buffer_pix(0, r, color)
        
        while x < y:
            if f >= 0:
                y -= 1
                dy += 2
                f += dy
            x += 1
            dx += 2
            f += dx
            
            set_buffer_pix(r + x, r + y, color)
            set_buffer_pix(r - x, r + y, color)
            set_buffer_pix(r + x, r - y, color)
            set_buffer_pix(r - x, r - y, color)
            set_buffer_pix(r + y, r + x, color)
            set_buffer_pix(r - y, r + x, color)
            set_buffer_pix(r + y, r - x, color)
            set_buffer_pix(r - y, r - x, color)
        
        self.gpu.block(x0, y0, x0 + diam, y0 + diam, buffer)
    
    @micropython.native
    def draw_box(self, x, y, width, height, color, bg_color = None, radius = None):
        if type(radius) == int and bg_color != None:
            self.draw_rounded_box(x, y, width, height, radius, color, bg_color)
        else:
            self.draw_normal_box(x, y, width, height, color)
    
    @micropython.native
    def draw_normal_box(self, x, y, w, h, color):
        """Draw a filled box (optimized for horizontal drawing).

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            w (int): Width of rectangle.
            h (int): Height of rectangle.
            color (int): RGB888 color value.
        """
        is_offgrid = self.is_off_grid(x, y, x + w - 1, y + h - 1)
        invalid_size = w == 0 or h == 0
        
        if is_offgrid or invalid_size:
            return
        
        chunk_height = 1024 // w
        chunk_count, remainder = divmod(h, chunk_height)
        chunk_size = chunk_height * w
        chunk_y = y
        if chunk_count:
            buf = color.to_bytes(3, 'big') * chunk_size
            for c in range(0, chunk_count):
                self.gpu.block(x, chunk_y, x + w - 1, chunk_y + chunk_height - 1, buf)
                chunk_y += chunk_height

        if remainder:
            buf = color.to_bytes(3, 'big') * remainder * w
            self.gpu.block(x, chunk_y, x + w - 1, chunk_y + remainder - 1, buf)
    
    @micropython.native
    def draw_rounded_box(self, pos_x, pos_y, width, height, radius, fill_color, background_color):
        size = (width * height)
        b_r, b_g, b_b = background_color.to_bytes(3, 'big')
        
        chunk_height = (1024 // width) - 1
        chunk_size = chunk_height * width
        
        buf = bytearray(fill_color.to_bytes(3, 'big') * chunk_size)
        chunk_y = 0
        
        square_radius = radius ** 2

        for y in range(height):
            if chunk_y >= chunk_height:
                chunk_y = 0
                
                self.gpu.block(pos_x, pos_y, pos_x + width - 1, pos_y + chunk_height - 1, buf)
                pos_y += chunk_height
                
                if chunk_height-1 >= height - y:
                    chunk_height = height - y
                    chunk_size = chunk_height * width
                
                buf = bytearray(fill_color.to_bytes(3, 'big') * chunk_size)

            top = (y < radius)
            bottom = (y >= height - radius)
            row = (chunk_y * width)

            in_top_radius = (radius - y) ** 2
            in_bottom_radius = (y - (height - radius)) ** 2

            for x in range(width):
                left = (x < radius)
                right = (x >= width - radius)

                left_top = (left and top)
                right_top = (right and top)
                left_bottom = (left and bottom)
                right_bottom = (right and bottom)

                in_left_radius = (radius - x) ** 2
                in_right_radius = ((width - radius) - x) ** 2

                if (
                    left_top and in_left_radius + in_top_radius > square_radius or
                    left_bottom and in_left_radius + in_bottom_radius > square_radius or
                    
                    right_top and in_right_radius + in_top_radius > square_radius or
                    right_bottom and in_right_radius + in_bottom_radius > square_radius
                ):                    
                    offset = ((row + x) * 3)
                    
                    buf[offset]     = b_r
                    buf[offset + 1] = b_g
                    buf[offset + 2] = b_b
            
            chunk_y += 1
            
        self.gpu.block(pos_x, pos_y, pos_x + width - 1, pos_y + height - 1, buf)
    
    def draw_circle_optmized(self, canvas_x, canvas_y, radius, color):
        pass
    
    @micropython.native
    def draw_circle(self, canvas_x, canvas_y, radius, color):
        threshold1 = radius
        threshold2 = 0
        x = radius
        y = 0
        
        while(x >= y):
            for i in range(2):
                x = -x
                for j in range(2):
                    y = -y
                    pos = (canvas_x + x, canvas_y + y)
                    self.draw_pixel(pos[0], pos[1], color)
                    self.draw_pixel(pos[1], pos[0], color)
            
            y += 1
            threshold1 = threshold1 + y
            threshold2 = threshold1 - x
            
            if threshold2 >= 0:
                threshold1 = threshold2
                x -= 1
            
            #print('x, y: ', x, y, 'threshold: ', threshold1, threshold2, 'predict: ', (((1+(8*(-threshold2)))**(1/2))-1)/2)
            #((n+1)*n)/2 = x
            #((n+1)*n)/2 = 49
            #49 = ((n-1)/n) ** 2
            #49**(1/2) = (n-1)/n
            #49**(1/2) * n = n - 1
            #(49**(1/2))-1 * n = - 1
            #N = (49**(1/2))-1) / -1
            #(((1+(8*21))**(1/2))-1)/2
            
    @micropython.native
    def draw_circle_alpha(self, x0, y0, r, color):
        """Draw a circle.

        Args:
            x0 (int): X coordinate of center point.
            y0 (int): Y coordinate of center point.
            r (int): Radius.
            color (int): RGB888 color value.
        """
        f = 1 - r
        dx = 1
        dy = -r - r
        x = 0
        y = r
        self.draw_pixel(x0, y0 + r, color)
        self.draw_pixel(x0, y0 - r, color)
        self.draw_pixel(x0 + r, y0, color)
        self.draw_pixel(x0 - r, y0, color)
        while x < y:
            if f >= 0:
                y -= 1
                dy += 2
                f += dy
            x += 1
            dx += 2
            f += dx
            self.draw_pixel(x0 + x, y0 + y, color)
            self.draw_pixel(x0 - x, y0 + y, color)
            self.draw_pixel(x0 + x, y0 - y, color)
            self.draw_pixel(x0 - x, y0 - y, color)
            self.draw_pixel(x0 + y, y0 + x, color)
            self.draw_pixel(x0 - y, y0 + x, color)
            self.draw_pixel(x0 + y, y0 - x, color)
            self.draw_pixel(x0 - y, y0 - x, color)

    def draw_ellipse(self, x0, y0, a, b, color):
        """Draw an ellipse.

        Args:
            x0, y0 (int): Coordinates of center point.
            a (int): Semi axis horizontal.
            b (int): Semi axis vertical.
            color (int): RGB888 color value.
        Note:
            The center point is the center of the x0,y0 pixel.
            Since pixels are not divisible, the axes are integer rounded
            up to complete on a full pixel.  Therefore the major and
            minor axes are increased by 1.
        """
        a2 = a * a
        b2 = b * b
        twoa2 = a2 + a2
        twob2 = b2 + b2
        x = 0
        y = b
        px = 0
        py = twoa2 * y
        # Plot initial points
        self.draw_pixel(x0 + x, y0 + y, color)
        self.draw_pixel(x0 - x, y0 + y, color)
        self.draw_pixel(x0 + x, y0 - y, color)
        self.draw_pixel(x0 - x, y0 - y, color)
        # Region 1
        p = round(b2 - (a2 * b) + (0.25 * a2))
        while px < py:
            x += 1
            px += twob2
            if p < 0:
                p += b2 + px
            else:
                y -= 1
                py -= twoa2
                p += b2 + px - py
            self.draw_pixel(x0 + x, y0 + y, color)
            self.draw_pixel(x0 - x, y0 + y, color)
            self.draw_pixel(x0 + x, y0 - y, color)
            self.draw_pixel(x0 - x, y0 - y, color)
        # Region 2
        p = round(b2 * (x + 0.5) * (x + 0.5) +
                  a2 * (y - 1) * (y - 1) - a2 * b2)
        while y > 0:
            y -= 1
            py -= twoa2
            if p > 0:
                p += a2 - py
            else:
                x += 1
                px += twob2
                p += a2 - py + px
            self.draw_pixel(x0 + x, y0 + y, color)
            self.draw_pixel(x0 - x, y0 + y, color)
            self.draw_pixel(x0 + x, y0 - y, color)
            self.draw_pixel(x0 - x, y0 - y, color)

    def draw_hline(self, x, y, w, color):
        """Draw a horizontal line.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            w (int): Width of line.
            color (int): RGB888 color value.
        """
        if self.is_off_grid(x, y, x + w - 1, y):
            return
        line = color.to_bytes(3, 'big') * w
        self.gpu.block(x, y, x + w - 1, y, line)
    
    @micropython.native
    def draw_bitmap(self, path, x=0, y=0, w=None, h=None):
        """Draw bitmap image from flash.

        Args:
            path (string): Bitmap Image file path.
            x (int): X coordinate of image left. Default is 0.
            y (int): Y coordinate of image top. Default is 0.
            w (int): Width of image. If not informed, loads from file.
            h (int): Height of image. If not informed, loads from file.
        """
        
        with open(path, "rb") as f:
            if not w or not h:
                f.seek(18)
                w = ustruct.unpack('<i', f.read(4))[0]

                f.seek(22)
                h = ustruct.unpack('<i', f.read(4))[0]
            
            x2 = x + w - 1
            y2 = y + h - 1
            if self.is_off_grid(x, y, x2, y2):
                f.close()
                return
            
            f.seek(54)
            
            chunk_height = 1024 // w
            chunk_count, remainder = divmod(h, chunk_height)
            chunk_size = chunk_height * w * 3
            chunk_y = y + chunk_height * chunk_count
            
            if chunk_count:
                for c in range(0, chunk_count):
                    buf = bytearray(f.read(chunk_size))
                    self.reverse(buf)
                    self.gpu.block(x, chunk_y, x2, chunk_y + chunk_height - 1, buf)
                    
                    chunk_y -= chunk_height
                    
            if remainder:
                buf = bytearray(remainder * w * 3)
                self.reverse(buf)
                self.gpu.block(x, chunk_y, x2, chunk_y + remainder - 1, buf)
                
            f.close()
    
    @micropython.native
    def draw_letter(self, x, y, letter, font, color, background=0, landscape=False, transparent=False):
        """Draw a letter.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            letter (string): Letter to draw.
            font (XglcdFont object): Font.
            color (int): RGB888 color value.
            background (int): RGB888 background color (default: black).
            landscape (bool): Orientation (default: False = portrait)
        """
        w, h = font.get_width_height(letter)
        
        if landscape:
            y -= w
            block = {'x':x, 'y':y, 'x2':x + h - 1, 'y2':y + w - 1}
        else:
            block = {'x':x, 'y':y, 'x2':x + w - 1, 'y2':y + h - 1}
        
        if self.is_off_grid(block['x'], block['y'], block['x2'], block['y2']):
            return 0, 0
        
        pixels = list(font.get_letter(letter, landscape))
        
        
        
        # Check for errors (Font could be missing specified letter)
        if len(pixels) == 0:
            return w, h
        
        if transparent:
            for pix in pixels:
                self.draw_pixel(block['x']+pix[0], block['y']+pix[1], color)
        else:
            buf = bytearray(background.to_bytes(3, 'big') * w * h)
            
            for pix in pixels:
                buf = self.set_buffer_pix(pix[0], pix[1], w, buf, color)
            
            self.gpu.block(block['x'], block['y'], block['x2'], block['y2'], buf)
        
        return w, h
    
    @micropython.native
    def draw_pixel(self, x, y, color):
        """Draw a single pixel.

        Args:
            x (int): X position.
            y (int): Y position.
            color (int): RGB888 color value.
        """
        if self.is_off_grid(x, y, x, y):
            return
        
        self.gpu.block(x, y, x, y, color.to_bytes(3, 'big'))
    
    @micropython.native
    def draw_text(self, x, y, text, font, color=Color.rgb(255, 255, 255),  background=Color.rgb(0, 0, 0), landscape=False, spacing=2, transparent=False):
        """Draw text.

        Args:
            x (int): Starting X position.
            y (int): Starting Y position.
            text (string): Text to draw.
            font (XglcdFont object): Font.
            color (int): RGB888 color value.
            background (int): RGB888 background color (default: black).
            landscape (bool): Orientation (default: False = portrait)
            spacing (int): Pixels between letters (default: 1)
        """
        cache = {}
        
        for letter in text:
            # Get letter array and letter dimensions
            
            w, h = self.draw_letter(x, y, letter, font, color, background, landscape, transparent)
            # Stop on error
            if w == 0 or h == 0:
                print('Invalid width {0} or height {1}'.format(w, h))
                return

            if landscape:
                # Fill in spacing
                if spacing and not transparent:
                    self.draw_box(x, y - w - spacing, h, spacing, background)
                
                # Position y for next letter
                y -= (w + spacing)
            else:
                # Fill in spacing
                if spacing and not transparent:
                    self.draw_box(x + w, y, spacing, h, background)
                
                # Position x for next letter
                x += (w + spacing)
                
    @micropython.native
    def is_off_grid(self, xmin, ymin, xmax, ymax):
        """Check if coordinates extend past display boundaries.

        Args:
            xmin (int): Minimum horizontal pixel.
            ymin (int): Minimum vertical pixel.
            xmax (int): Maximum horizontal pixel.
            ymax (int): Maximum vertical pixel.
        Returns:
            boolean: False = Coordinates OK, True = Error.
        """
        if xmin < 0:
            return True
        if ymin < 0:
            return True
        if xmax >= self.gpu.width:
            return True
        if ymax >= self.gpu.height:
            return True
        
        return False
    
    def clear(self, color = 0, lines = 8):
        self.gpu.clear(color, lines)
    