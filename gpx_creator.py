#!/usr/bin/env python3
"""
GPX Creator - A GUI application to create GPX files

Copyright (c) 2025 Douglas Carroll

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative Commons,
PO Box 1866, Mountain View, CA 94042, USA.

You are free to:
- Share: copy and redistribute the material in any medium or format
- Adapt: remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- Attribution: You must give appropriate credit, provide a link to the license, and indicate
  if changes were made.
- ShareAlike: If you remix, transform, or build upon the material, you must distribute your
  contributions under the same license as the original.

No additional restrictions: You may not apply legal terms or technological measures that
legally restrict others from doing anything the license permits.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import webbrowser


class GPXCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GPX Creator")
        self.root.geometry("500x300")
        
        # Variables
        self.time_var = tk.StringVar()
        self.minlat_var = tk.StringVar()
        self.minlon_var = tk.StringVar()
        self.maxlat_var = tk.StringVar()
        self.maxlon_var = tk.StringVar()
        self.wpt_lat_var = tk.StringVar()
        self.wpt_lon_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.sym_var = tk.StringVar(value="WayPoint")
        
        # Set default time to current time
        self.time_var.set(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z")
        
        # Set up trace callbacks to auto-populate bounds from waypoint
        self.wpt_lat_var.trace_add("write", self.update_bounds_from_waypoint)
        self.wpt_lon_var.trace_add("write", self.update_bounds_from_waypoint)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Time field
        ttk.Label(main_frame, text="Time (UTC):").grid(row=0, column=0, sticky=tk.W, pady=5)
        time_entry = ttk.Entry(main_frame, textvariable=self.time_var, width=30)
        time_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Now", command=self.set_current_time).grid(row=0, column=2, padx=5)
        
        # Waypoint section
        ttk.Label(main_frame, text="Waypoint:", font=("", 10, "bold")).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        ttk.Label(main_frame, text="Latitude:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.wpt_lat_var, width=20).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(main_frame, text="Longitude:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.wpt_lon_var, width=20).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Name field
        ttk.Label(main_frame, text="Name:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Create GPX File", command=self.create_gpx_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        
        # Copyright notice
        copyright_frame = ttk.Frame(main_frame)
        copyright_frame.grid(row=6, column=0, columnspan=3, pady=(15, 0))
        ttk.Label(copyright_frame, text=f"© {datetime.now().year} Douglas Carroll — ", font=("", 9)).pack(side=tk.LEFT)
        link_label = ttk.Label(copyright_frame, text="svburnttoast.com", font=("", 9), foreground="blue", cursor="hand2")
        link_label.pack(side=tk.LEFT)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("https://svburnttoast.com/"))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def is_decimal_degrees(self, value):
        """Check if value is in decimal degrees format"""
        if not value or not value.strip():
            return False
        try:
            num = float(value.strip())
            return True
        except ValueError:
            return False
    
    def detect_coordinate_format(self, value):
        """Detect the format of a coordinate string"""
        if not value or not value.strip():
            return None
        
        value = value.strip()
        
        # Check if it's already decimal degrees
        if self.is_decimal_degrees(value):
            return "decimal"
        
        # Check for DMS format (degrees° minutes' seconds" or degrees minutes seconds)
        # Patterns: 33°14'11" or 33 14 11 or 33-14-11 or 33°14'11.5" or 33° 14' 11"
        dms_pattern = r'^(-?\d+)[°\s\-]+\s*(\d+)[\'\s\-]+\s*(\d+(?:\.\d+)?)["\s]*([NSEW])?$'
        match = re.match(dms_pattern, value, re.IGNORECASE)
        if match:
            return "dms"
        
        # Check for DM format (degrees° minutes' or degrees minutes)
        # Patterns: 33°14.5' or 33 14.5 or 33-14.5 or 33° 14.5'
        dm_pattern = r'^(-?\d+)[°\s\-]+\s*(\d+(?:\.\d+)?)[\'\s]*([NSEW])?$'
        match = re.match(dm_pattern, value, re.IGNORECASE)
        if match:
            return "dm"
        
        return None
    
    def convert_dms_to_decimal(self, value):
        """Convert degrees/minutes/seconds to decimal degrees"""
        value = value.strip()
        # Pattern: degrees° minutes' seconds" [NSEW] (hyphens treated as separators)
        pattern = r'^(-?\d+)[°\s\-]+\s*(\d+)[\'\s\-]+\s*(\d+(?:\.\d+)?)["\s]*([NSEW])?$'
        match = re.match(pattern, value, re.IGNORECASE)
        if not match:
            return None
        
        degrees = float(match.group(1))
        minutes = float(match.group(2))
        seconds = float(match.group(3))
        direction = match.group(4)
        
        decimal = abs(degrees) + minutes / 60.0 + seconds / 3600.0
        
        # Apply sign based on direction or original sign
        if direction:
            if direction.upper() in ['S', 'W']:
                decimal = -decimal
        elif degrees < 0:
            decimal = -decimal
        
        return decimal
    
    def convert_dm_to_decimal(self, value):
        """Convert degrees/minutes to decimal degrees"""
        value = value.strip()
        # Pattern: degrees° minutes' [NSEW] (hyphens treated as separators)
        pattern = r'^(-?\d+)[°\s\-]+\s*(\d+(?:\.\d+)?)[\'\s]*([NSEW])?$'
        match = re.match(pattern, value, re.IGNORECASE)
        if not match:
            return None
        
        degrees = float(match.group(1))
        minutes = float(match.group(2))
        direction = match.group(3)
        
        decimal = abs(degrees) + minutes / 60.0
        
        # Apply sign based on direction or original sign
        if direction:
            if direction.upper() in ['S', 'W']:
                decimal = -decimal
        elif degrees < 0:
            decimal = -decimal
        
        return decimal
    
    def validate_and_convert_coordinate(self, value, coord_type="latitude"):
        """Validate coordinate format and offer conversion if needed"""
        if not value or not value.strip():
            return None, False
        
        value = value.strip()
        
        # Check if already in decimal degrees format
        if self.is_decimal_degrees(value):
            try:
                num = float(value)
                # Validate range
                if coord_type == "latitude" and (-90 <= num <= 90):
                    return num, True
                elif coord_type == "longitude" and (-180 <= num <= 180):
                    return num, True
                else:
                    return None, False
            except ValueError:
                return None, False
        
        # Detect format
        format_type = self.detect_coordinate_format(value)
        
        if format_type is None:
            return None, False
        
        # Try to convert
        converted = None
        if format_type == "dms":
            converted = self.convert_dms_to_decimal(value)
        elif format_type == "dm":
            converted = self.convert_dm_to_decimal(value)
        
        if converted is None:
            return None, False
        
        # Validate range after conversion
        if coord_type == "latitude" and not (-90 <= converted <= 90):
            return None, False
        elif coord_type == "longitude" and not (-180 <= converted <= 180):
            return None, False
        
        return converted, True
    
    def update_bounds_from_waypoint(self, *args):
        """Auto-populate bounds from waypoint lat/lon"""
        wpt_lat = self.wpt_lat_var.get()
        wpt_lon = self.wpt_lon_var.get()
        
        if wpt_lat:
            self.minlat_var.set(wpt_lat)
            self.maxlat_var.set(wpt_lat)
        
        if wpt_lon:
            self.minlon_var.set(wpt_lon)
            self.maxlon_var.set(wpt_lon)
    
    def set_current_time(self):
        """Set time to current UTC time"""
        self.time_var.set(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z")
    
    def clear_fields(self):
        """Clear all input fields"""
        self.time_var.set(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z")
        self.minlat_var.set("")
        self.minlon_var.set("")
        self.maxlat_var.set("")
        self.maxlon_var.set("")
        self.wpt_lat_var.set("")
        self.wpt_lon_var.set("")
        self.name_var.set("")
        self.sym_var.set("WayPoint")
    
    def validate_fields(self):
        """Validate that required fields are filled and coordinates are in correct format"""
        if not self.time_var.get():
            messagebox.showerror("Error", "Time is required")
            return False
        
        if not all([self.wpt_lat_var.get(), self.wpt_lon_var.get()]):
            messagebox.showerror("Error", "Waypoint latitude and longitude are required")
            return False
        
        if not self.name_var.get():
            messagebox.showerror("Error", "Name is required")
            return False
        
        # Validate and convert latitude
        lat_value = self.wpt_lat_var.get()
        lat_decimal, is_valid = self.validate_and_convert_coordinate(lat_value, "latitude")
        
        if not is_valid:
            messagebox.showerror(
                "Invalid Latitude Format",
                "Latitude must be in decimal degrees format (e.g., 33.14711).\n\n"
                "Valid range: -90 to 90 degrees.\n\n"
                "Supported alternative formats:\n"
                "- Degrees/Minutes/Seconds: 33°14'11\"\n"
                "- Degrees/Minutes: 33°14.5'"
            )
            return False
        
        # If conversion was needed, apply converted value automatically
        if not self.is_decimal_degrees(lat_value):
            self.wpt_lat_var.set(f"{lat_decimal:.6f}")
        
        # Validate and convert longitude
        lon_value = self.wpt_lon_var.get()
        lon_decimal, is_valid = self.validate_and_convert_coordinate(lon_value, "longitude")
        
        if not is_valid:
            messagebox.showerror(
                "Invalid Longitude Format",
                "Longitude must be in decimal degrees format (e.g., -79.13536).\n\n"
                "Valid range: -180 to 180 degrees.\n\n"
                "Supported alternative formats:\n"
                "- Degrees/Minutes/Seconds: 79°8'7\"\n"
                "- Degrees/Minutes: 79°8.1'"
            )
            return False
        
        # If conversion was needed, apply converted value automatically
        if not self.is_decimal_degrees(lon_value):
            self.wpt_lon_var.set(f"{lon_decimal:.6f}")
        
        # Ensure bounds are populated from waypoint
        self.update_bounds_from_waypoint()
        
        # Ensure symbol has default value
        if not self.sym_var.get():
            self.sym_var.set("WayPoint")
        
        return True
    
    def create_gpx_file(self):
        """Create GPX file from user input"""
        if not self.validate_fields():
            return
        
        # Ensure bounds are populated from waypoint (in case validation didn't trigger it)
        self.update_bounds_from_waypoint()
        
        # Ask for save location; suggest filename from Name field
        default_name = self.name_var.get().strip()
        for c in r'\/:*?"<>|':
            default_name = default_name.replace(c, "_")
        if not default_name:
            default_name = "waypoint"
        filename = filedialog.asksaveasfilename(
            defaultextension=".gpx",
            filetypes=[("GPX files", "*.gpx"), ("All files", "*.*")],
            initialfile=default_name
        )
        
        if not filename:
            return
        
        try:
            # Create GPX root element
            gpx = ET.Element("gpx")
            gpx.set("creator", "Burnt Toast GPX Creator")
            gpx.set("version", "1.1")
            gpx.set("xmlns", "http://www.topografix.com/GPX/1/1")
            gpx.set("xmlns:uuidx", "http://www.garmin.com/xmlschemas/IdentifierExtension/v1")
            gpx.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema")
            gpx.set("xsi:schemaLocation", 
                   "http://www.topografix.com/GPX/1/1 https://www.topografix.com/GPX/1/1/gpx.xsd "
                   "http://www.garmin.com/xmlschemas/IdentifierExtension/v1 "
                   "http://www.garmin.com/xmlschemas/IdentifierExtension.xsd")
            
            # Metadata
            metadata = ET.SubElement(gpx, "metadata")
            
            # Author
            author = ET.SubElement(metadata, "author")
            name = ET.SubElement(author, "name")
            name.text = "Burnt Toast"
            email = ET.SubElement(author, "email")
            email.set("id", "doug")
            email.set("domain", "svburnttoast.com")
            
            # Copyright
            copyright_elem = ET.SubElement(metadata, "copyright")
            copyright_elem.set("author", "Douglas Carroll")
            year = ET.SubElement(copyright_elem, "year")
            year.text = str(datetime.now().year)
            
            # Link
            link = ET.SubElement(metadata, "link")
            link.set("href", "https://svburnttoast.com/")
            text = ET.SubElement(link, "text")
            text.text = "SV Burnt Toast"
            
            # Time
            time_elem = ET.SubElement(metadata, "time")
            time_elem.text = self.time_var.get()
            
            # Bounds
            bounds = ET.SubElement(metadata, "bounds")
            bounds.set("minlat", self.minlat_var.get())
            bounds.set("minlon", self.minlon_var.get())
            bounds.set("maxlat", self.maxlat_var.get())
            bounds.set("maxlon", self.maxlon_var.get())
            
            # Waypoint
            wpt = ET.SubElement(gpx, "wpt")
            wpt.set("lat", self.wpt_lat_var.get())
            wpt.set("lon", self.wpt_lon_var.get())
            
            name_elem = ET.SubElement(wpt, "name")
            name_elem.text = self.name_var.get()
            
            desc = ET.SubElement(wpt, "desc")
            
            sym = ET.SubElement(wpt, "sym")
            sym.text = self.sym_var.get()
            
            # Extensions
            extensions = ET.SubElement(wpt, "extensions")
            uuid_elem = ET.SubElement(extensions, "uuidx:uuid")
            uuid_elem.text = str(uuid.uuid4())
            
            # Create XML tree and format it
            tree = ET.ElementTree(gpx)
            
            # Pretty print XML
            xml_str = ET.tostring(gpx, encoding='unicode')
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent="  ")
            
            # Remove extra blank lines
            lines = [line for line in pretty_xml.split('\n') if line.strip()]
            formatted_xml = '\n'.join(lines)
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_xml)
            
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create GPX file:\n{str(e)}")


def main():
    root = tk.Tk()
    app = GPXCreatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

