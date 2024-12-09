from subprocess import run

import cv2


def screenshot():
    path = "/tmp/test.png"
    run(["scrot", "-u", "-o", path])
    return path


def get_focused_window_pos():
    out = run(["xdotool", "getwindowfocus", "getwindowgeometry"], capture_output=True)
    return out.stdout.decode("utf-8").splitlines()[1].strip().split(" ")[1].split(",")


def get_interactable_nodes():
    # Load the image
    image = cv2.imread(screenshot())
    print("screenshot done")
    x, y = get_focused_window_pos()
    x_offset = int(x)
    y_offset = int(y)

    # Define the threshold value for detecting text and button regions
    threshold = 50

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Otsu's global thresholding method to separate foreground from background
    _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find contours in the image using the detected regions as masks
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Define a function to classify each contour based on its shape and size
    def classify_contour(contour):
        # Compute the area of the contour
        area = cv2.contourArea(contour)

        # If the area is less than 50 pixels, it's likely a button or icon
        if area < 50:
            return "button"

        # Otherwise, it's likely to be a text field or folder label
        else:
            return "text"

    # Initialize a list to store the center coordinates of each detected element
    elements = set()

    # Iterate over each contour and classify it
    for contour in contours:
        # Get the bounding box of the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Classify the contour based on its shape and size
        classification = classify_contour(contour)

        # If it's a button or icon, compute the center coordinates and add them to the list
        if classification == "button":
            cx = x + w / 2
            cy = y + h / 2
            # elements.append({"x": cx + x_offset, "y": cy + y_offset})
            elements.add((cx + x_offset, cy + y_offset))

    # Print the list of detected elements in JSON format
    return elements
