import os
import sqlite3
import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from openai import OpenAI


class ImageAnalysisDB:
    """Manages SQLite database for storing image analysis results"""
    
    def __init__(self, db_path: str = "data/image_analysis.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database and create table if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                image_filename TEXT NOT NULL,
                summary TEXT,
                items TEXT,
                persons TEXT,
                places TEXT,
                things TEXT,
                other_details TEXT,
                raw_response TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(image_path)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def insert_analysis(self, analysis_data: Dict) -> bool:
        """Insert analysis results into database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO image_analyses 
                (image_path, image_filename, summary, items, persons, places, things, other_details, raw_response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_data.get('image_path'),
                analysis_data.get('image_filename'),
                analysis_data.get('summary'),
                analysis_data.get('items'),
                analysis_data.get('persons'),
                analysis_data.get('places'),
                analysis_data.get('things'),
                analysis_data.get('other_details'),
                analysis_data.get('raw_response')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    def get_all_analyses(self):
        """Retrieve all analyses from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM image_analyses ORDER BY analyzed_at DESC")
        results = cursor.fetchall()
        conn.close()
        return results


class ImageAnalyzer:
    """Handles image analysis using GPT-4o API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = None
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            # Try to get from environment variable
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_image(self, image_path: str) -> Dict:
        """Analyze image using GPT-4o and return structured data"""
        if not self.client:
            raise ValueError("OpenAI client not initialized. Please provide API key.")
        
        # Encode image
        base64_image = self.encode_image(image_path)
        
        # Create detailed prompt for structured analysis
        prompt = """Analyze this image in detail and provide a comprehensive analysis. 
        Please structure your response as a JSON object with the following fields:
        
        {
            "summary": "A brief 2-3 sentence summary of what the image shows",
            "items": "A comma-separated list of all distinct items, objects, or elements visible in the image",
            "persons": "A comma-separated list of any people visible (or 'None' if no people)",
            "places": "A comma-separated list of any locations, settings, or environments visible (or 'None' if not applicable)",
            "things": "A comma-separated list of inanimate objects, items, or things visible",
            "other_details": "Any other relevant details such as colors, mood, time of day, weather, activities, text visible, etc."
        }
        
        Be thorough and specific. If a category doesn't apply, use 'None'. Return ONLY valid JSON, no additional text."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3  # Lower temperature for more consistent, factual responses
            )
            
            # Extract response
            response_text = response.choices[0].message.content
            
            # Try to parse JSON from response
            try:
                # Sometimes the response might have markdown code blocks
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                analysis_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured response manually
                analysis_data = {
                    "summary": response_text[:200] if len(response_text) > 200 else response_text,
                    "items": "Unable to parse",
                    "persons": "Unable to parse",
                    "places": "Unable to parse",
            "things": "Unable to parse",
                    "other_details": response_text
                }
            
            # Add metadata
            analysis_data['image_path'] = image_path
            analysis_data['image_filename'] = os.path.basename(image_path)
            analysis_data['raw_response'] = response_text
            
            return analysis_data
            
        except Exception as e:
            raise Exception(f"API Error: {str(e)}")


class ImageAnalysisGUI:
    """GUI application for image analysis"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Image Content Analysis with GPT-4o")
        self.root.geometry("800x600")
        
        # Initialize components
        self.db = ImageAnalysisDB()
        self.analyzer = None
        
        # Check for API key
        self.check_api_key()
        
        self.setup_ui()
    
    def check_api_key(self):
        """Check if API key is available"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            messagebox.showwarning(
                "API Key Missing",
                "OPENAI_API_KEY environment variable not set.\n\n"
                "Please set it before using the application:\n"
                "export OPENAI_API_KEY='your-key-here'"
            )
        else:
            try:
                self.analyzer = ImageAnalyzer(api_key=api_key)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to initialize OpenAI client: {e}")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Select Image", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=60).grid(row=0, column=0, padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).grid(row=0, column=1, padx=5)
        
        # Analysis button
        self.analyze_btn = ttk.Button(
            main_frame, 
            text="Analyze Image", 
            command=self.analyze_image,
            state=tk.DISABLED if not self.analyzer else tk.NORMAL
        )
        self.analyze_btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Text area for results
        self.results_text = tk.Text(results_frame, height=15, width=80, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Database info
        db_info_frame = ttk.Frame(main_frame)
        db_info_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        ttk.Button(db_info_frame, text="View All Analyses", command=self.view_database).grid(row=0, column=0, padx=5)
        ttk.Button(db_info_frame, text="Database Location", command=self.show_db_location).grid(row=0, column=1, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def browse_file(self):
        """Open file dialog to select image"""
        file_path = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.analyze_btn.config(state=tk.NORMAL if self.analyzer else tk.DISABLED)
    
    def analyze_image(self):
        """Analyze selected image"""
        image_path = self.file_path_var.get()
        
        if not image_path or not os.path.exists(image_path):
            messagebox.showerror("Error", "Please select a valid image file.")
            return
        
        if not self.analyzer:
            messagebox.showerror("Error", "OpenAI API key not configured.")
            return
        
        # Disable button during analysis
        self.analyze_btn.config(state=tk.DISABLED)
        self.status_var.set("Analyzing image...")
        self.results_text.delete(1.0, tk.END)
        self.root.update()
        
        try:
            # Analyze image
            analysis_data = self.analyzer.analyze_image(image_path)
            
            # Save to database
            if self.db.insert_analysis(analysis_data):
                self.status_var.set("Analysis complete and saved to database!")
            else:
                self.status_var.set("Analysis complete but database save failed.")
            
            # Display results
            self.display_results(analysis_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze image: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
        finally:
            self.analyze_btn.config(state=tk.NORMAL)
    
    def display_results(self, analysis_data: Dict):
        """Display analysis results in text area"""
        self.results_text.delete(1.0, tk.END)
        
        output = f"""
IMAGE ANALYSIS RESULTS
{'=' * 60}

File: {analysis_data.get('image_filename', 'N/A')}
Path: {analysis_data.get('image_path', 'N/A')}
Analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 60}
SUMMARY
{'=' * 60}
{analysis_data.get('summary', 'N/A')}

{'=' * 60}
ITEMS DETECTED
{'=' * 60}
{analysis_data.get('items', 'N/A')}

{'=' * 60}
PERSONS
{'=' * 60}
{analysis_data.get('persons', 'N/A')}

{'=' * 60}
PLACES
{'=' * 60}
{analysis_data.get('places', 'N/A')}

{'=' * 60}
THINGS
{'=' * 60}
{analysis_data.get('things', 'N/A')}

{'=' * 60}
OTHER DETAILS
{'=' * 60}
{analysis_data.get('other_details', 'N/A')}

{'=' * 60}
"""
        
        self.results_text.insert(1.0, output)
    
    def view_database(self):
        """Open window to view all database entries"""
        window = tk.Toplevel(self.root)
        window.title("All Image Analyses")
        window.geometry("900x600")
        
        # Create treeview
        tree = ttk.Treeview(window, columns=("Filename", "Summary", "Analyzed At"), show="headings")
        tree.heading("Filename", text="Filename")
        tree.heading("Summary", text="Summary")
        tree.heading("Analyzed At", text="Analyzed At")
        
        tree.column("Filename", width=200)
        tree.column("Summary", width=400)
        tree.column("Analyzed At", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate with data
        analyses = self.db.get_all_analyses()
        for analysis in analyses:
            tree.insert("", tk.END, values=(
                analysis[2],  # filename
                analysis[3][:100] + "..." if analysis[3] and len(analysis[3]) > 100 else analysis[3] or "N/A",  # summary
                analysis[11]  # analyzed_at
            ))
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_db_location(self):
        """Show database file location"""
        db_path = os.path.abspath(self.db.db_path)
        messagebox.showinfo("Database Location", f"Database location:\n{db_path}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ImageAnalysisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
