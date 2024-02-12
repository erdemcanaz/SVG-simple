import base64
import svgwrite
import cv2
from io import BytesIO
import os 
import xml.etree.ElementTree as ET


class MultiSVGCreator:
    def __init__(self):
        self.drawings = {}

    def create_new_drawing(self, filename:str=None, size=('2480px', '3508px')):
        """
        Create or modify an SVG drawing. Resizes the existing SVG if it exists, or creates a new one.

        :param filename: The name of the file to save the SVG as.
        :param size: The size of the SVG canvas.
        """
        if filename in self.drawings:
            raise Exception(f"There is already an svg file named as {filename}")        

        self.drawings[filename] = svgwrite.Drawing(filename=filename, size=size)     

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

    def save_all(self):
        """
        Save all SVG drawings to their respective files.
        """
        for drawing in self.drawings.values():
            drawing.save()


# Usage example            
if __name__ == '__main__':
    svg_creator = MultiSVGCreator()
    svg_creator.create_new_drawing(filename= 'example2.svg')
    #svg_creator.add_circle('example1.svg', (100, 100), 80, fill='green', stroke='orange')

    href= "C:\\Users\\Levovo20x\\Documents\\GitHub\\SVG-simple\\nature.png"
    svg_creator.embed_image(filename="example2.svg", insert=(0,0),size=('1200px', '630px'), href=href)

    cv2_image = cv2.imread("nature.png", cv2.IMREAD_COLOR)
    svg_creator.embed_cv2_image(filename = "example2.svg", insert= (0,1000), size =('1200px', '630px'), cv2_image = cv2_image)

    svg_creator.save_all()

