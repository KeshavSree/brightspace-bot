import pygame
import sys
import time
import os
import platform

# Import pyperclip for clipboard operations
try:
    import pyperclip
    has_pyperclip = True
except ImportError:
    print("pyperclip module not found. Installing...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"])
        import pyperclip
        has_pyperclip = True
        print("pyperclip installed successfully!")
    except Exception as e:
        print(f"Could not install pyperclip: {e}")
        print("For copy/paste functionality, please install pyperclip manually:")
        print("pip install pyperclip")
        has_pyperclip = False
# Theme colors - white, bright gray, and orange
THEME_WHITE = (255, 255, 255)
THEME_GRAY = (240, 240, 245)
THEME_ORANGE = (255, 128, 0)
THEME_ORANGE_LIGHT = (255, 160, 64)
THEME_ORANGE_DARK = (220, 110, 0)
THEME_TEXT = (55, 55, 55)

class TextInput:
    def __init__(self, x, y, width, height, font_size=24, max_length=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.font = pygame.font.Font(None, font_size)
        self.text_color = THEME_TEXT
        self.bg_color = THEME_WHITE
        self.border_color = (200, 200, 200)
        self.focused_border_color = THEME_ORANGE
        self.selection_color = (255, 200, 150, 150)  # Semi-transparent orange
        self.cursor_pos = 0
        self.max_length = max_length
        
        # Text selection
        self.selection_start = None
        self.selecting = False
        self.dragging = False
        
        # Cursor blinking
        self.cursor_visible = True
        self.cursor_toggle_time = 0.5  # seconds
        self.last_toggle_time = time.time()
        
        # Focus state
        self.focused = False
        
        # Animation for focus
        self.border_alpha = 0
        self.target_alpha = 0
    
    def get_char_position_from_mouse(self, x):
        """Determine character position based on mouse x coordinate"""
        if x <= self.rect.x + 10:
            return 0
        
        text_width = self.font.size(self.text)[0]
        if x >= self.rect.x + 10 + text_width:
            return len(self.text)
        
        x_rel = x - (self.rect.x + 10)
        for i in range(len(self.text) + 1):
            if self.font.size(self.text[:i])[0] >= x_rel:
                return i - 1 if i > 0 else 0
        
        return len(self.text)
    
    def get_selected_text(self):
        """Get currently selected text"""
        if self.selection_start is None:
            return ""
        
        start = min(self.selection_start, self.cursor_pos)
        end = max(self.selection_start, self.cursor_pos)
        return self.text[start:end]
    
    def delete_selected_text(self):
        """Delete the selected text"""
        if self.selection_start is None:
            return
        
        start = min(self.selection_start, self.cursor_pos)
        end = max(self.selection_start, self.cursor_pos)
        
        self.text = self.text[:start] + self.text[end:]
        self.cursor_pos = start
        self.selection_start = None
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            prev_focus = self.focused
            self.focused = self.rect.collidepoint(event.pos)
            
            # Update focus animation target
            self.target_alpha = 255 if self.focused else 0
            
            if self.focused:
                # Set cursor position based on click position
                self.cursor_pos = self.get_char_position_from_mouse(event.pos[0])
                
                # Start selection on mouse down with shift key
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                else:
                    # Clear selection unless starting a new selection with mouse drag
                    self.selection_start = self.cursor_pos
                    self.selecting = True
            else:
                # Clear selection when clicking outside
                self.selection_start = None

        elif event.type == pygame.MOUSEMOTION:
            # Handle text selection with mouse drag
            if self.selecting and pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(event.pos):
                    self.cursor_pos = self.get_char_position_from_mouse(event.pos[0])
                    # If this is the first drag event after mouse down, set selection start
                    if self.selection_start == self.cursor_pos:
                        self.selecting = False  # Not actually selecting text yet
                
        elif event.type == pygame.MOUSEBUTTONUP:
            # End selection
            if self.selecting:
                self.selecting = False
                if self.selection_start == self.cursor_pos:
                    self.selection_start = None  # Cancel selection if no movement
        
        if event.type == pygame.KEYDOWN and self.focused:
            # Key modifiers
            mods = pygame.key.get_mods()
            ctrl_pressed = mods & (pygame.KMOD_CTRL | pygame.KMOD_META)  # Ctrl on Windows/Linux, Cmd on Mac
            shift_pressed = mods & pygame.KMOD_SHIFT
            
            # Handle keyboard shortcuts
            if ctrl_pressed:
                if event.key == pygame.K_a:  # Select all
                    self.selection_start = 0
                    self.cursor_pos = len(self.text)
                    return False
                elif event.key == pygame.K_c:  # Copy
                    selected_text = self.get_selected_text()
                    if selected_text and has_pyperclip:
                        try:
                            pyperclip.copy(selected_text)
                        except Exception as e:
                            print(f"Copy failed: {e}")
                    return False
                elif event.key == pygame.K_x:  # Cut
                    selected_text = self.get_selected_text()
                    if selected_text and has_pyperclip:
                        try:
                            pyperclip.copy(selected_text)
                            self.delete_selected_text()
                        except Exception as e:
                            print(f"Cut failed: {e}")
                    elif selected_text:
                        self.delete_selected_text()  # Still delete even if copy fails
                    return False
                elif event.key == pygame.K_v:  # Paste
                    if has_pyperclip:
                        try:
                            clipboard_text = pyperclip.paste()
                            
                            # Delete selected text first if there's a selection
                            if self.selection_start is not None:
                                self.delete_selected_text()
                            
                            # Limit pasted text to max length
                            remaining_space = self.max_length - len(self.text)
                            if remaining_space > 0:
                                clipboard_text = clipboard_text[:remaining_space]
                                self.text = self.text[:self.cursor_pos] + clipboard_text + self.text[self.cursor_pos:]
                                self.cursor_pos += len(clipboard_text)
                        except Exception as e:
                            print(f"Paste failed: {e}")
                    return False
            
            # Handle normal keys
            if event.key == pygame.K_BACKSPACE:
                if self.selection_start is not None:
                    self.delete_selected_text()
                elif self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.selection_start is not None:
                    self.delete_selected_text()
                elif self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                if shift_pressed:
                    # Start selection or extend existing selection
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                else:
                    # If there's a selection and we're not extending it, move to start of selection
                    if self.selection_start is not None:
                        self.cursor_pos = min(self.selection_start, self.cursor_pos)
                        self.selection_start = None
                    else:
                        self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                if shift_pressed:
                    # Start selection or extend existing selection
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
                else:
                    # If there's a selection and we're not extending it, move to end of selection
                    if self.selection_start is not None:
                        self.cursor_pos = max(self.selection_start, self.cursor_pos)
                        self.selection_start = None
                    else:
                        self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                if shift_pressed:
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    self.cursor_pos = 0
                else:
                    self.cursor_pos = 0
                    self.selection_start = None
            elif event.key == pygame.K_END:
                if shift_pressed:
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    self.cursor_pos = len(self.text)
                else:
                    self.cursor_pos = len(self.text)
                    self.selection_start = None
            elif event.key == pygame.K_RETURN:
                # Return can trigger submit if needed
                return True
            else:
                # For regular character input, replace selection if there is one
                if event.unicode.isprintable():
                    if self.selection_start is not None:
                        self.delete_selected_text()
                    
                    # Add character if not at max length
                    if len(self.text) < self.max_length:
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
            
        # Smooth animation for focus border
        if self.border_alpha < self.target_alpha:
            self.border_alpha = min(self.border_alpha + 15, self.target_alpha)
        elif self.border_alpha > self.target_alpha:
            self.border_alpha = max(self.border_alpha - 15, self.target_alpha)
    
    def draw(self, surface):
        # Draw background with rounded corners
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=5)
        
        # Draw animated border with alpha blending
        if self.focused:
            # Create a surface for the border with alpha
            border_color = list(self.focused_border_color)
            border_color.append(self.border_alpha)  # Add alpha value
            border_rect = self.rect.inflate(4, 4)  # Slightly larger rect for glow effect
            pygame.draw.rect(surface, border_color, border_rect, width=2, border_radius=7)
        
        # Draw solid border
        border_color = self.focused_border_color if self.focused else self.border_color
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=5)
        
        # Calculate text positioning
        text_padding = 10  # Increased padding for better appearance
        clip_rect = pygame.Rect(self.rect.x + text_padding, self.rect.y + 2, 
                               self.rect.width - text_padding * 2, self.rect.height - 4)
        
        # Draw selection highlight if there is a selection
        if self.selection_start is not None and self.text:
            start = min(self.selection_start, self.cursor_pos)
            end = max(self.selection_start, self.cursor_pos)
            
            # Calculate selection rectangle
            if start < len(self.text) and start != end:
                start_x = self.rect.x + text_padding + self.font.size(self.text[:start])[0]
                width = self.font.size(self.text[start:end])[0]
                
                # Draw selection rectangle
                select_rect = pygame.Rect(start_x, self.rect.y + 5, width, self.rect.height - 10)
                pygame.draw.rect(surface, self.selection_color, select_rect, border_radius=2)
        
        # Draw text
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(midleft=(self.rect.x + text_padding, self.rect.centery))
            
            # Make sure text doesn't overflow
            if text_rect.width > self.rect.width - (text_padding * 2):
                # Calculate offset to show the cursor if it's at the end
                if self.cursor_pos >= len(self.text) - 5:
                    # Show the end of the text with the cursor
                    offset = text_rect.width - (self.rect.width - (text_padding * 2))
                    text_rect.x -= offset
                else:
                    # Show text centered around cursor position
                    cursor_width = self.font.size(self.text[:self.cursor_pos])[0]
                    visible_width = self.rect.width - (text_padding * 2)
                    if cursor_width > visible_width / 2:
                        offset = cursor_width - (visible_width / 2)
                        text_rect.x -= offset
            
            # Set clip area to prevent drawing outside the text box
            original_clip = surface.get_clip()
            surface.set_clip(clip_rect)
            surface.blit(text_surface, text_rect)
            surface.set_clip(original_clip)
        
        # Draw cursor when visible and focused
        if self.focused and self.cursor_visible:
            if self.text:
                cursor_x = self.rect.x + text_padding + self.font.size(self.text[:self.cursor_pos])[0]
            else:
                cursor_x = self.rect.x + text_padding
            
            # Check if cursor is visible within the clipping area
            if cursor_x >= clip_rect.left and cursor_x <= clip_rect.right:
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
    def __init__(self, x, y, width, height, text, corner_radius=8):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.corner_radius = corner_radius
        
        # Button states and colors - using the theme orange colors
        self.normal_color = THEME_ORANGE
        self.hover_color = THEME_ORANGE_LIGHT
        self.pressed_color = THEME_ORANGE_DARK
        self.text_color = THEME_WHITE
        
        # Current state
        self.hovered = False
        self.pressed = False
        
        # Animation
        self.shadow_offset = 3
        self.shadow_alpha = 100
        
        # Font
        self.font = pygame.font.Font(None, 26)  # Slightly larger font
    
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
            shadow_offset = 0  # No shadow when pressed
        elif self.hovered:
            color = self.hover_color
            shadow_offset = self.shadow_offset + 1  # Larger shadow on hover
        else:
            color = self.normal_color
            shadow_offset = self.shadow_offset
        
        # Draw shadow
        if shadow_offset > 0:
            shadow_rect = self.rect.copy()
            shadow_rect.y += shadow_offset
            shadow_color = (0, 0, 0, self.shadow_alpha)
            pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=self.corner_radius)
        
        # Draw the button with rounded corners
        pygame.draw.rect(surface, color, self.rect, border_radius=self.corner_radius)
        
        # Draw subtle inner highlight
        if not self.pressed:
            highlight_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, 
                                       self.rect.width - 4, 5)
            highlight_color = (255, 255, 255, 40)  # Very subtle white
            pygame.draw.rect(surface, highlight_color, highlight_rect, 
                           border_radius=self.corner_radius)
        
        # Draw text with slight shadow for depth
        if self.pressed:
            # Text appears "pressed" by shifting down slightly
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.centery + 1))
        else:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Add subtle text shadow for better readability
        shadow_surface = self.font.render(self.text, True, (0, 0, 0, 128))
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)

class Application:
    def __init__(self):
        # Initialize pygame modules
        # Initialize pygame modules
        pygame.init()
        pygame.font.init()
        # Setup window with title
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Brightspace Bot Interface")
        
        # Set window icon if available
        try:
            icon = pygame.Surface((32, 32))
            icon.fill(THEME_ORANGE)
            pygame.display.set_icon(icon)
        except:
            pass  # Icon setting is not critical
        
        # Colors
        self.bg_color = THEME_GRAY
        
        # UI components with improved positioning
        self.text_input = TextInput(200, 260, 400, 40)
        self.submit_button = Button(340, 320, 120, 40, "Submit")
        
        # App title
        self.title_font = pygame.font.Font(None, 36)
        self.title_text = "Brightspace Bot"
        
        # Status message
        self.status_font = pygame.font.Font(None, 20)
        self.status_text = "Ready"
        self.status_color = (100, 100, 100)
        self.status_timer = 0
        
        # Clock for frame rate
        self.clock = pygame.time.Clock()
        self.running = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Check for text input events
            submission = self.text_input.handle_event(event)
            if submission:
                self.on_submit()
            
            # Check for button events
            if self.submit_button.handle_event(event):
                self.on_submit()
    
    def on_submit(self):
        # This is where we'll integrate with browser automation later
        submitted_text = self.text_input.get_text()
        if submitted_text:
            print(f"Submitted: {submitted_text}")
            # Update status message
            self.status_text = f"Sent: {submitted_text[:20]}{'...' if len(submitted_text) > 20 else ''}"
            self.status_color = (50, 120, 50)  # Green for success
            self.status_timer = 3  # Display for 3 seconds
            
            # Placeholder for future browser integration
            # For now, just clear the input after submission
            self.text_input.text = ""
            self.text_input.cursor_pos = 0
        else:
            # Show error if empty submission
            self.status_text = "Error: Cannot submit empty text"
            self.status_color = (180, 50, 50)  # Red for error
            self.status_timer = 3  # Display for 3 seconds
    
    def update(self):
        # Update text input
        self.text_input.update()
        
        # Update status message timer
        if self.status_timer > 0:
            self.status_timer -= 1/60  # 60 FPS
            if self.status_timer <= 0:
                self.status_text = "Ready"
                self.status_color = (100, 100, 100)
    
    def draw(self):
        # Clear screen
        self.screen.fill(self.bg_color)
        
        # Draw title
        title_surface = self.title_font.render(self.title_text, True, THEME_ORANGE)
        title_rect = title_surface.get_rect(center=(400, 150))
        self.screen.blit(title_surface, title_rect)
        
        # Draw components
        self.text_input.draw(self.screen)
        self.submit_button.draw(self.screen)
        
        # Draw status message
        status_surface = self.status_font.render(self.status_text, True, self.status_color)
        status_rect = status_surface.get_rect(center=(400, 380))
        self.screen.blit(status_surface, status_rect)
        
        # Draw hint text
        # Draw hint text
        if has_pyperclip:
            hint_text = "Tip: Use Ctrl+V to paste, Ctrl+C to copy selected text"
            if platform.system() == 'Darwin':  # macOS
                hint_text = "Tip: Use ⌘+V to paste, ⌘+C to copy selected text"
        else:
            hint_text = "Tip: Install pyperclip for clipboard support"
            
        # Render the hint text surface
        hint_surface = self.status_font.render(hint_text, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(center=(400, 410))
        self.screen.blit(hint_surface, hint_rect)
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
