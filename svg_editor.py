import base64
import svgwrite
import cv2
from io import BytesIO
import os 
import xml.etree.ElementTree as ET
from PIL import Image

class MultiSVGCreator:
    def __init__(self):
        self.drawings = {}

    COLOR_PALETTE = {
        "light_blue": "rgb(125, 206, 237)",
        "dark_blue": "rgb(0, 96, 169)",
        "dark_blue_2": "rgb(0, 51, 204)",
        "black": "rgb(0, 0, 0)",
        "white": "rgb(255, 255, 255)"
    }

    def create_new_drawing(self, filename:str=None, size=('1244', '1756px')):
        """        
        Create or modify an SVG drawing. Resizes the existing SVG if it exists, or creates a new one.

        :param filename: The name of the file to save the SVG as.
        :param size: The size of the SVG canvas.
        #300DPI : size=('2480px', '3508px')
        #150DPI : size=('1244px', '1756px')
        """
        if filename in self.drawings:
            raise Exception(f"There is already an svg file named as {filename}")        

        self.SIZE = size
        self.drawings[filename] = svgwrite.Drawing(filename=filename, size=size)     

    def get_size(self):
        return self.SIZE
    
    def add_rectangle(self, filename, insert, size, fill='none', stroke='black'):
        """
        Add a rectangle to an SVG drawing.
        
        :param filename: The filename of the SVG to add the rectangle to.
        :param insert: A tuple (x, y) for the top-left corner of the rectangle.
        :param size: A tuple (width, height) for the size of the rectangle.
        :param fill: The fill color of the rectangle.
        :param stroke: The stroke color of the rectangle.
        """
        if filename in self.drawings:
            self.drawings[filename].add(self.drawings[filename].rect(insert=insert, size=size, fill=fill, stroke=stroke))

    def add_circle(self, filename, center, radius, fill='none', stroke='black'):
        """
        Add a circle to an SVG drawing.
        
        :param filename: The filename of the SVG to add the circle to.
        :param center: A tuple (cx, cy) for the center of the circle.
        :param radius: The radius of the circle.
        :param fill: The fill color of the circle.
        :param stroke: The stroke color of the circle.
        """
        if filename in self.drawings:
            self.drawings[filename].add(self.drawings[filename].circle(center=center, r=radius, fill=fill, stroke=stroke))

    def link_image(self, filename, insert, size, href):
        """
        Link an image to an SVG drawing.
        
        :param filename: The filename of the SVG to add the image to.
        :param insert: A tuple (x, y) for the top-left corner of the image.
        :param size: A tuple (width, height) for the size of the image.
        :param href: The path or URL to the image file.
        """
        if filename in self.drawings:
            self.drawings[filename].add(self.drawings[filename].image(href=href, insert=insert, size=size))

    def embed_image(self, filename, insert, size, href):
        """
        Embed an image into an SVG drawing.

        :param filename: The filename of the SVG to add the image to.
        :param insert: A tuple (x, y) for the top-left corner of the image.
        :param size: A tuple (width, height) for the size of the image.
        :param href: The path to the image file.
        """
        if filename in self.drawings:
            # Read the image file and encode it as base64
            with open(href, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Determine the image's MIME type based on its extension
            # You may need to add other image formats as necessary
            mime_type = "image/jpeg"  # Default to JPEG
            if href.lower().endswith('.png'):
                mime_type = "image/png"
            elif href.lower().endswith('.gif'):
                mime_type = "image/gif"
            elif href.lower().endswith('.svg'):
                mime_type = "image/svg+xml"
            
            # Construct the data URI
            data_uri = f"data:{mime_type};base64,{image_data}"
            
            # Embed the image data in the SVG
            self.drawings[filename].add(self.drawings[filename].image(href=data_uri, insert=insert, size=size))
    
    def embed_image_low_resolution(self, filename, insert, size, href):
        """
        Embed a lower resolution image into an SVG drawing, using updated Pillow resampling method.

        :param filename: The filename of the SVG to add the image to.
        :param insert: A tuple (x, y) for the top-left corner of the image.
        :param size: A tuple (width, height) in pixels for the target size of the image.
        :param href: The path to the image file.
        """
        if filename in self.drawings:
            # Open and resize the image to the desired dimensions
            with Image.open(href) as img:
                # Convert size from SVG dimensions (which may include units like 'px') to integers
                target_size = (int(size[0].replace('px', '')), int(size[1].replace('px', '')))
                
                # Use Image.Resampling.LANCZOS for high-quality downsampling
                resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
                
                # Convert the resized image to bytes
                img_byte_arr = BytesIO()
                img_format = img.format if img.format else 'JPEG'  # Default format if not detected
                resized_img.save(img_byte_arr, format=img_format)
                
                # Encode the image file as base64
                image_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            
            # Determine the image's MIME type
            mime_type = f"image/{img_format.lower()}"
            
            # Construct the data URI
            data_uri = f"data:{mime_type};base64,{image_data}"
            
            # Embed the resized and encoded image data in the SVG
            self.drawings[filename].add(self.drawings[filename].image(href=data_uri, insert=insert, size=size))
            
    def embed_cv2_image(self, filename, insert, size, cv2_image):
        """
        Embed an OpenCV image into an SVG drawing.

        :param filename: The filename of the SVG to add the image to.
        :param insert: A tuple (x, y) for the top-left corner of the image.
        :param size: A tuple (width, height) for the size of the image.
        :param cv2_image: The OpenCV image (NumPy array).
        """
        if filename in self.drawings:
            # Convert the OpenCV image to PNG format in memory
            _, buffer = cv2.imencode('.png', cv2_image)
            
            # Encode the PNG image data as base64
            image_data = base64.b64encode(buffer).decode('utf-8')
            
            # Construct the data URI
            data_uri = f"data:image/png;base64,{image_data}"
            
            # Embed the image data in the SVG
            self.drawings[filename].add(self.drawings[filename].image(href=data_uri, insert=insert, size=size))

    def embed_cv2_image_adjustable_resolution(self, filename, insert, size, cv2_image, constant_proportions = False, quality_factor = 1.0):
        """
        Embed a lower resolution OpenCV image into an SVG drawing.

        :param filename: The filename of the SVG to add the image to.
        :param insert: A tuple (x, y) for the top-left corner of the image.
        :param size: A tuple (width, height) in pixels for the target size of the image.
        :param cv2_image: The OpenCV image (NumPy array).
        :constant_proportions: Whether the image proportions are preserved or not while resizing
        :quality_factor: by increasing this value, the quality of the embeded image is increased but the size of the document is increased.
        """
        if filename in self.drawings:
            # Convert size from SVG dimensions (which may include units like 'px') to integers
            target_width = int(size[0].replace('px', ''))
            target_height = int(size[1].replace('px', ''))
            
        resized_image = None
        height, width = cv2_image.shape[:2]
        
        if constant_proportions:
            # Calculate the scale factor to maintain aspect ratio
            height, width = cv2_image.shape[:2]
            scale_w = target_width / width
            scale_h = target_height / height
            scale = min(scale_w, scale_h)

            # Calculate new dimensions
            new_width = int(quality_factor * width * scale)
            new_height = int(quality_factor * height * scale)

            # Resize the image
            resized_image = cv2.resize(cv2_image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        else:
            # Resize without preserving aspect ratio
            target_width = int(quality_factor * target_width)
            target_height = int(quality_factor * target_height)
            resized_image = cv2.resize(cv2_image, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)        
            
        # Convert the resized OpenCV image to PNG format in memory
        _, buffer = cv2.imencode('.png', resized_image)
        
        # Encode the PNG image data as base64
        image_data = base64.b64encode(buffer).decode('utf-8')
        
        # Construct the data URI
        data_uri = f"data:image/png;base64,{image_data}"
        
        # Embed the image data in the SVG
        self.drawings[filename].add(self.drawings[filename].image(href=data_uri, insert=insert, size=size))

    def save_all(self):
        """
        Save all SVG drawings to their respective files.
        """
        for drawing in self.drawings.values():
            drawing.save()

# Usage example            
if __name__ == '__main__':
    svg_creator = MultiSVGCreator()
    svg_creator.create_new_drawing(filename= 'rendered_svg_files/page_1.svg')
    #svg_creator.add_circle('example1.svg', (100, 100), 80, fill='green', stroke='orange')

    cover_page_template_href = "C:\\Users\\Levovo20x\\Documents\\GitHub\\SVG-simple\\templates\\cover_page_template.png"
    svg_creator.embed_image(filename = 'rendered_svg_files/page_1.svg', insert=(0,0), size=svg_creator.get_size(), href = cover_page_template_href)

    href= "C:\\Users\\Levovo20x\\Documents\\GitHub\\SVG-simple\\nature.png"
    svg_creator.embed_image(filename='rendered_svg_files/page_1.svg', insert=(0,0),size=('100px', '100px'), href=href)
    svg_creator.embed_image_low_resolution(filename='rendered_svg_files/page_1.svg', insert=(0,100),size=('100px', '100px'), href=href)

    cv2_image = cv2.imread("nature.png", cv2.IMREAD_COLOR)
    svg_creator.embed_cv2_image(filename = 'rendered_svg_files/page_1.svg', insert= (0,200), size =('100px', '100px'), cv2_image = cv2_image)
    svg_creator.embed_cv2_image_adjustable_resolution(filename = 'rendered_svg_files/page_1.svg', insert= (0,300), size =('100px', '100px'), cv2_image = cv2_image, constant_proportions= True, quality_factor= 3)

    svg_creator.save_all()

