"""
Graphical User Interface for CLANK! Tracker

Real-time monitoring GUI built with tkinter for gameplay tracking.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import sys
from pathlib import Path
from PIL import Image, ImageTk
import json

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from screen_capture import ScreenCapture
from ocr_processor import OCRProcessor
from game_tracker import GameTracker


class ClankTrackerGUI:
    """Main GUI application class"""
    
    def __init__(self, root):
        """Initialize the GUI application"""
        self.root = root
        self.root.title("CLANK! Tracker - Real-time Game Monitoring")
        self.root.geometry("800x600")
        
        # Initialize components
        self.screen_capture = None
        self.ocr_processor = None
        self.game_tracker = None
        
        # GUI state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.last_screenshot = None
        
        # Create GUI elements
        self.create_widgets()
        self.initialize_components()
    
    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🎮 CLANK! Tracker", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Control Panel
        self.create_control_panel(main_frame)
        
        # Status Panel
        self.create_status_panel(main_frame)
        
        # Main Content Area (tabs)
        self.create_content_tabs(main_frame)
        
        # Bottom Status Bar
        self.create_status_bar(main_frame)
    
    def create_control_panel(self, parent):
        """Create control buttons panel"""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="5")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Monitoring controls
        self.start_button = ttk.Button(
            control_frame, 
            text="▶️ Start Monitoring", 
            command=self.start_monitoring
        )
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_button = ttk.Button(
            control_frame, 
            text="⏹️ Stop Monitoring", 
            command=self.stop_monitoring,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Manual capture
        ttk.Button(
            control_frame, 
            text="📸 Capture Now", 
            command=self.manual_capture
        ).grid(row=0, column=2, padx=5)
        
        # Settings
        ttk.Button(
            control_frame, 
            text="⚙️ Settings", 
            command=self.open_settings
        ).grid(row=0, column=3, padx=5)
        
        # Save session
        ttk.Button(
            control_frame, 
            text="💾 Save Session", 
            command=self.save_session
        ).grid(row=0, column=4, padx=(5, 0))
    
    def create_status_panel(self, parent):
        """Create status information panel"""
        status_frame = ttk.LabelFrame(parent, text="Status", padding="5")
        status_frame.grid(row=1, column=3, sticky=(tk.W, tk.E, tk.N), padx=(10, 0), pady=(0, 10))
        
        # Status labels
        self.status_label = ttk.Label(status_frame, text="🔴 Not monitoring")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.cards_label = ttk.Label(status_frame, text="Cards detected: 0")
        self.cards_label.grid(row=1, column=0, sticky=tk.W)
        
        self.events_label = ttk.Label(status_frame, text="Events tracked: 0")
        self.events_label.grid(row=2, column=0, sticky=tk.W)
        
        self.duration_label = ttk.Label(status_frame, text="Session: 00:00:00")
        self.duration_label.grid(row=3, column=0, sticky=tk.W)
    
    def create_content_tabs(self, parent):
        """Create tabbed content area"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Screenshot tab
        self.create_screenshot_tab()
        
        # Cards tab  
        self.create_cards_tab()
        
        # Events tab
        self.create_events_tab()
        
        # Session tab
        self.create_session_tab()
    
    def create_screenshot_tab(self):
        """Create screenshot display tab"""
        screenshot_frame = ttk.Frame(self.notebook)
        self.notebook.add(screenshot_frame, text="📸 Screenshot")
        
        # Image display
        self.image_label = ttk.Label(screenshot_frame, text="No screenshot yet")
        self.image_label.pack(expand=1, fill="both", padx=10, pady=10)
        
        # Image controls
        img_controls = ttk.Frame(screenshot_frame)
        img_controls.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(
            img_controls, 
            text="Load Image", 
            command=self.load_image
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            img_controls, 
            text="Save Screenshot", 
            command=self.save_screenshot
        ).pack(side="left", padx=5)
        
        ttk.Button(
            img_controls, 
            text="Process OCR", 
            command=self.process_current_image
        ).pack(side="left", padx=5)
    
    def create_cards_tab(self):
        """Create detected cards tab"""
        cards_frame = ttk.Frame(self.notebook)
        self.notebook.add(cards_frame, text="🎴 Cards")
        
        # Cards list
        self.cards_tree = ttk.Treeview(
            cards_frame, 
            columns=("timestamp", "confidence"), 
            show="tree headings"
        )
        self.cards_tree.heading("#0", text="Card Name")
        self.cards_tree.heading("timestamp", text="Time Detected")
        self.cards_tree.heading("confidence", text="Confidence")
        
        self.cards_tree.pack(expand=1, fill="both", padx=10, pady=10)
        
        # Cards scrollbar
        cards_scrollbar = ttk.Scrollbar(cards_frame, orient="vertical", command=self.cards_tree.yview)
        self.cards_tree.configure(yscrollcommand=cards_scrollbar.set)
        cards_scrollbar.pack(side="right", fill="y")
    
    def create_events_tab(self):
        """Create game events tab"""
        events_frame = ttk.Frame(self.notebook)
        self.notebook.add(events_frame, text="🎯 Events")
        
        # Events list
        self.events_tree = ttk.Treeview(
            events_frame,
            columns=("timestamp", "type", "description"),
            show="tree headings"
        )
        self.events_tree.heading("#0", text="ID")
        self.events_tree.heading("timestamp", text="Timestamp")
        self.events_tree.heading("type", text="Event Type")
        self.events_tree.heading("description", text="Description")
        
        self.events_tree.pack(expand=1, fill="both", padx=10, pady=10)
        
        # Events scrollbar
        events_scrollbar = ttk.Scrollbar(events_frame, orient="vertical", command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=events_scrollbar.set)
        events_scrollbar.pack(side="right", fill="y")
    
    def create_session_tab(self):
        """Create session report tab"""
        session_frame = ttk.Frame(self.notebook)
        self.notebook.add(session_frame, text="📊 Session")
        
        # Session report text area
        self.session_text = scrolledtext.ScrolledText(
            session_frame,
            wrap=tk.WORD,
            width=60,
            height=20
        )
        self.session_text.pack(expand=1, fill="both", padx=10, pady=10)
        
        # Session controls
        session_controls = ttk.Frame(session_frame)
        session_controls.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Button(
            session_controls,
            text="🔄 Refresh Report",
            command=self.update_session_report
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            session_controls,
            text="📤 Export Report",
            command=self.export_session_report
        ).pack(side="left", padx=5)
    
    def create_status_bar(self, parent):
        """Create bottom status bar"""
        self.status_bar = ttk.Label(
            parent, 
            text="Ready to start monitoring", 
            relief="sunken"
        )
        self.status_bar.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E))
    
    def initialize_components(self):
        """Initialize tracker components"""
        try:
            self.status_bar.config(text="Initializing components...")
            self.root.update()
            
            self.screen_capture = ScreenCapture()
            self.ocr_processor = OCRProcessor()
            self.game_tracker = GameTracker()
            
            self.status_bar.config(text="Components initialized successfully")
            self.update_session_report()
            
        except Exception as e:
            self.status_bar.config(text=f"Initialization failed: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize components:\n{e}")
    
    def start_monitoring(self):
        """Start automatic monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            
            # Update UI
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="🟢 Monitoring active")
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            self.status_bar.config(text="Monitoring started")
    
    def stop_monitoring(self):
        """Stop automatic monitoring"""
        if self.monitoring_active:
            self.monitoring_active = False
            
            # Update UI
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.status_label.config(text="🔴 Not monitoring")
            
            self.status_bar.config(text="Monitoring stopped")
    
    def monitoring_loop(self):
        """Main monitoring loop (runs in separate thread)"""
        while self.monitoring_active:
            try:
                # Capture screenshot
                screenshot = self.screen_capture.capture_game_area()
                self.last_screenshot = screenshot
                
                # Update screenshot display (thread-safe)
                self.root.after(0, self.update_screenshot_display, screenshot)
                
                # Process OCR
                cards = self.ocr_processor.extract_card_names(screenshot)
                
                if cards:
                    # Track detected cards
                    timestamp = time.strftime("%H:%M:%S")
                    screenshot_path = f"screenshot_{timestamp.replace(':', '')}.png"
                    
                    self.game_tracker.track_card_detection(cards, screenshot_path)
                    
                    # Update UI (thread-safe)
                    self.root.after(0, self.update_cards_display)
                    self.root.after(0, self.update_status_display)
                
                # Wait before next capture (5 seconds)
                time.sleep(5)
                
            except Exception as e:
                self.root.after(0, lambda: self.status_bar.config(text=f"Monitoring error: {e}"))
                break
    
    def manual_capture(self):
        """Manually capture and process screenshot"""
        try:
            screenshot = self.screen_capture.capture_game_area()
            self.last_screenshot = screenshot
            
            self.update_screenshot_display(screenshot)
            
            # Process OCR
            cards = self.ocr_processor.extract_card_names(screenshot)
            
            if cards:
                self.game_tracker.track_card_detection(cards, "manual_capture.png")
                self.update_cards_display()
                self.update_status_display()
                self.status_bar.config(text=f"Manual capture: found {len(cards)} cards")
            else:
                self.status_bar.config(text="Manual capture: no cards detected")
                
        except Exception as e:
            messagebox.showerror("Capture Error", f"Failed to capture screenshot:\n{e}")
    
    def update_screenshot_display(self, screenshot):
        """Update screenshot display"""
        try:
            # Resize image for display
            display_size = (400, 300)
            display_image = screenshot.copy()
            display_image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(display_image)
            
            # Update label
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
            
        except Exception as e:
            self.image_label.config(text=f"Display error: {e}")
    
    def update_cards_display(self):
        """Update cards tree view"""
        # Clear existing items
        for item in self.cards_tree.get_children():
            self.cards_tree.delete(item)
        
        # Add current cards
        for card in self.game_tracker.current_session['cards_seen']:
            timestamp = card['timestamp'].split('T')[1].split('.')[0]  # Extract time part
            self.cards_tree.insert(
                "", "end",
                text=card['card_name'],
                values=(timestamp, card['confidence'])
            )
    
    def update_events_display(self):
        """Update events tree view"""
        # Clear existing items
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        # Add current events
        for i, event in enumerate(self.game_tracker.current_session['game_events']):
            timestamp = event['timestamp'].split('T')[1].split('.')[0]  # Extract time part
            self.events_tree.insert(
                "", "end",
                text=str(i + 1),
                values=(timestamp, event['event_type'], event['description'])
            )
    
    def update_status_display(self):
        """Update status labels"""
        if self.game_tracker:
            stats = self.game_tracker.get_session_stats()
            
            self.cards_label.config(text=f"Cards detected: {stats['unique_cards_seen']}")
            self.events_label.config(text=f"Events tracked: {stats['total_events']}")
            self.duration_label.config(text=f"Session: {stats['duration']}")
    
    def update_session_report(self):
        """Update session report text"""
        if self.game_tracker:
            report = self.game_tracker.generate_session_report()
            
            self.session_text.delete(1.0, tk.END)
            self.session_text.insert(1.0, report)
    
    def load_image(self):
        """Load image file for processing"""
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                image = Image.open(file_path)
                self.last_screenshot = image
                self.update_screenshot_display(image)
                self.status_bar.config(text=f"Loaded: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load image:\n{e}")
    
    def save_screenshot(self):
        """Save current screenshot"""
        if self.last_screenshot:
            file_path = filedialog.asksaveasfilename(
                title="Save Screenshot",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            
            if file_path:
                try:
                    self.last_screenshot.save(file_path)
                    self.status_bar.config(text=f"Screenshot saved: {Path(file_path).name}")
                except Exception as e:
                    messagebox.showerror("Save Error", f"Failed to save screenshot:\n{e}")
        else:
            messagebox.showwarning("No Screenshot", "No screenshot to save")
    
    def process_current_image(self):
        """Process current image with OCR"""
        if self.last_screenshot:
            try:
                cards = self.ocr_processor.extract_card_names(self.last_screenshot)
                
                if cards:
                    self.game_tracker.track_card_detection(cards, "processed_image.png")
                    self.update_cards_display()
                    self.update_status_display()
                    self.status_bar.config(text=f"OCR found {len(cards)} cards")
                else:
                    self.status_bar.config(text="OCR: no cards detected")
                    
            except Exception as e:
                messagebox.showerror("OCR Error", f"Failed to process image:\n{e}")
        else:
            messagebox.showwarning("No Image", "No image to process")
    
    def save_session(self):
        """Save current session"""
        try:
            filepath = self.game_tracker.save_session()
            messagebox.showinfo("Session Saved", f"Session saved to:\n{filepath}")
            self.status_bar.config(text="Session saved successfully")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save session:\n{e}")
    
    def export_session_report(self):
        """Export session report to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Session Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                report = self.game_tracker.generate_session_report()
                with open(file_path, 'w') as f:
                    f.write(report)
                
                messagebox.showinfo("Report Exported", f"Report exported to:\n{file_path}")
                self.status_bar.config(text="Report exported successfully")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export report:\n{e}")
    
    def open_settings(self):
        """Open settings dialog"""
        # Placeholder for settings dialog
        messagebox.showinfo("Settings", "Settings dialog not yet implemented")
    
    def on_closing(self):
        """Handle application closing"""
        if self.monitoring_active:
            self.stop_monitoring()
        
        # Save session before closing
        try:
            if self.game_tracker:
                self.game_tracker.save_session()
        except:
            pass
        
        self.root.destroy()


def main():
    """Main GUI entry point"""
    root = tk.Tk()
    app = ClankTrackerGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()