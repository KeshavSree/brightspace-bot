import pygame
import sys
import time

class TextInput:
    def __init__(self, x, y, width, height, font_size=24, max_length=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.font = pygame.font.Font(None, font_size)
        self.text_color = (0, 0, 0)
        self.bg_color = (255, 255, 255)
        self.border_color = (0, 0, 0)
        self.focused_border_color = (0, 120, 215)
        self.cursor_pos = 0
        self.max_length = max_length
        
        # Cursor blinking
        self.cursor_visible = True
        self.cursor_toggle_time = 0.5  # seconds
        self.last_toggle_time = time.time()
        
        # Focus state
        self.focused = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle focus when clicked
            self.focused = self.rect.collidepoint(event.pos)
            if self.focused:
                # Set cursor position based on click position
                x = event.pos[0]
                text_width = self.font.size(self.text)[0]
                if x <= self.rect.x + 5:
                    self.cursor_pos = 0
                elif x >= self.rect.x + text_width + 5:
                    self.cursor_pos = len(self.text)
                else:
                    # Approximate position based on click
                    x_rel = x - (self.rect.x + 5)
                    for i in range(len(self.text) + 1):
                        if self.font.size(self.text[:i])[0] >= x_rel:
                            self.cursor_pos = i - 1 if i > 0 else 0
                            break
        
        if event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_BACKSPACE:
                # Handle backspace
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                # Handle delete
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                # Move cursor left
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                # Move cursor right
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                # Move cursor to start
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                # Move cursor to end
                self.cursor_pos = len(self.text)
            elif event.key == pygame.K_RETURN:
                # Return can trigger submit if needed
                return True
            else:
                # Add character if not at max length
                if len(self.text) < self.max_length and event.unicode.isprintable():
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += 1
            
            # Reset cursor blink timer on any key press
            self.cursor_visible = True
            self.last_toggle_time = time.time()
        
        return False  # No submission
    
    def update(self):
        # Update cursor blinking
        current_time = time.time()
        if current_time - self.last_toggle_time > self.cursor_toggle_time:
            self.cursor_visible = not self.cursor_visible
            self.last_toggle_time = current_time
    
    def draw(self, surface):
        # Draw background and border
        pygame.draw.rect(surface, self.bg_color, self.rect)
        border_color = self.focused_border_color if self.focused else self.border_color
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        # Draw text
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
            
            # Make sure text doesn't overflow
            if text_rect.width > self.rect.width - 10:
                # Adjust to show end of text with cursor
                offset = text_rect.width - (self.rect.width - 10)
                text_rect.x -= offset
            
            surface.blit(text_surface, text_rect)
        
        # Draw cursor when visible and focused
        if self.focused and self.cursor_visible:
            if self.text:
                cursor_x = self.rect.x + 5 + self.font.size(self.text[:self.cursor_pos])[0]
            else:
                cursor_x = self.rect.x + 5
            
            pygame.draw.line(
                surface,
                self.text_color,
                (cursor_x, self.rect.y + 5),
                (cursor_x, self.rect.y + self.rect.height - 5),
                2
            )
    
    def get_text(self):
        return self.text

class Button:
    def __init__(self, x, y, width, height, text, corner_radius=5):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.corner_radius = corner_radius
        
        # Button states and colors
        self.normal_color = (100, 100, 255)
        self.hover_color = (120, 120, 255)
        self.pressed_color = (80, 80, 235)
        self.text_color = (255, 255, 255)
        
        # Current state
        self.hovered = False
        self.pressed = False
        
        # Font
        self.font = pygame.font.Font(None, 24)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Check hover state
            self.hovered = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                self.pressed = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            clicked = self.pressed and self.hovered
            self.pressed = False
            return clicked
        
        return False
    
    def draw(self, surface):
        # Determine current color based on state
        if self.pressed and self.hovered:
            color = self.pressed_color
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.normal_color
        
        # Draw the button with rounded corners
        pygame.draw.rect(surface, color, self.rect, border_radius=self.corner_radius)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class Application:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        
        # Setup window
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Brightspace Bot Interface")
        
        # Colors
        self.bg_color = (240, 240, 240)
        
        # UI components
        self.text_input = TextInput(200, 260, 400, 40)
        self.submit_button = Button(340, 320, 120, 40, "Submit")
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.running = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Check for text input events
            self.text_input.handle_event(event)
            
            # Check for button events
            if self.submit_button.handle_event(event):
                self.on_submit()
    
    def on_submit(self):
        # This is where we'll integrate with browser automation later
        submitted_text = self.text_input.get_text()
        print(f"Submitted: {submitted_text}")
        # Placeholder for future browser integration
        # For now, just clear the input after submission
        self.text_input.text = ""
        self.text_input.cursor_pos = 0
    
    def update(self):
        self.text_input.update()
    
    def draw(self):
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw components
        self.text_input.draw(self.screen)
        self.submit_button.draw(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(60)  # 60 FPS
        except Exception as e:
            print(f"Error: {e}")
        finally:
            pygame.quit()
            sys.exit()

# Run the application
if __name__ == "__main__":
    app = Application()
    app.run()

