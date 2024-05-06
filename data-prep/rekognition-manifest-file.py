# Adapted from AWS documentation

# Before running this, I used regex in VS Code to remove lines that were empty by replacing \n\n with \n

from datetime import datetime, timezone
import argparse
import logging
import json
import csv
import os
import re


"""
Purpose
Amazon Rekognition Custom Labels model example used in the service documentation.
Shows how to create an object detection manifest file from a CSV file.
You can specify multiple object annotations per image.
CSV file format is
filename,width,height,class,xmin,ymin,xmax,ymax,...
If necessary, use the bucket argument to specify the S3 bucket folder for the images.
https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/md-gt-cl-transform.html
"""

def check_duplicates(csv_file, deduplicated_file, duplicates_file):
    duplicates_found = False

    # Find duplicates.
    with open(csv_file, 'r', newline='') as f, \
            open(deduplicated_file, 'w') as dedup, \
            open(duplicates_file, 'w') as duplicates:

        reader = csv.reader(f)
        dedup_writer = csv.writer(dedup)
        duplicates_writer = csv.writer(duplicates)

        entries = set()

        for row in reader:
            key = tuple(row)
            if key not in entries:
                dedup_writer.writerow(row)
                entries.add(key)
            else:
                duplicates_writer.writerow(row)
                duplicates_found = True

    if not duplicates_found:
        os.remove(duplicates_file)
        os.remove(deduplicated_file)

    return duplicates_found

def split_row(row):
    """
    Splits the row based on the position of the "100,100" pattern.
    """
    width_index = row.index("100")
    height_index = width_index + 1

    file_name = ','.join(row[:width_index])
    width = row[width_index]
    height = row[height_index]
    class_name = row[height_index + 1]
    xmin = row[height_index + 2]
    ymin = row[height_index + 3]
    xmax = row[height_index + 4]
    ymax = row[height_index + 5]

    return file_name, width, height, class_name, xmin, ymin, xmax, ymax

    # Before (input):
        # filename,width,height,class,xmin,ymin,xmax,ymax
        # show_picture_asp?id=aaaaaaaaaaogcqq&w2=420&h2=378&clip=center,420,378&meta=0_jpg.rf.60ca1bb806ed39f9a829b5c1788dbe4c.jpg,100,100,Corn Gray leaf spot,1,1,99,88

    # After (output):
        # filename,width,height,class,xmin,ymin,xmax,ymax
        # show_picture_asp?id=aaaaaaaaaaogcqq&w2=420&h2=378&clip=center,420,378&meta=0_jpg.rf.60ca1bb806ed39f9a829b5c1788dbe4c.jpg|100|100|Corn Gray leaf spot|1|1|99|88
def create_json_line(file_name, width, height, annotations, class_name, s3_path):
    """
    Creates a JSON line for an image annotation.
    :param file_name: The name of the image file.
    :param width: The width of the image.
    :param height: The height of the image.
    :param annotations: The list of annotations for the image.
    :param class_name: The class name for the annotations.
    :param s3_path: The S3 path to the folder that contains the images.
    :return: The JSON line string.
    """
    source_ref = os.path.join(s3_path, file_name)

    # Create JSON for image source ref.
    json_line = {'source-ref': source_ref}

    bounding_box = {
        'annotations': annotations,
        'image_size': [{'width': int(width), 'depth': 3, 'height': int(height)}]
    }

    metadata = {
        'job-name': 'labeling-job/' + class_name,
        'class-map': {0: class_name},
        'human-annotated': "yes",
        'creation-date': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f'),
        'type': "groundtruth/object-detection",
        'objects': [{'confidence': 1} for _ in annotations]
    }

    json_line['bounding-box-metadata'] = metadata
    json_line['bounding-box'] = bounding_box

    return json.dumps(json_line)

def create_manifest_file(csv_file, manifest_file, s3_path):
    """
    Reads a CSV file and creates a Custom Labels object detection manifest file.
    :param csv_file: The source CSV file.
    :param manifest_file: The name of the manifest file to create.
    :param s3_path: The S3 path to the folder that contains the images.
    """
    logging.info("Processing CSV file %s", csv_file)

    image_count = 0
    label_count = 0

    image_annotations = {}

    with open(csv_file, newline='', encoding="UTF-8") as csvfile, \
            open(manifest_file, "w", encoding="UTF-8") as output_file:

        reader = csv.reader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        next(reader)  # Skip the header row

        for row in reader:
            print(f"Processing row: {row}")

            file_name, width, height, class_name, xmin, ymin, xmax, ymax = split_row(row)

            print(f"File name: {file_name}")

            if file_name not in image_annotations:
                image_annotations[file_name] = {
                    'width': int(width),
                    'height': int(height),
                    'class_name': class_name,
                    'annotations': []
                }

            image_annotations[file_name]['annotations'].append({
                'class_id': 0,  # Single class
                'left': int(xmin),
                'top': int(ymin),
                'width': int(xmax) - int(xmin),
                'height': int(ymax) - int(ymin)
            })

        for file_name, image_data in image_annotations.items():
            json_line = create_json_line(file_name,
                                         image_data['width'],
                                         image_data['height'],
                                         image_data['annotations'],
                                         image_data['class_name'],
                                         s3_path)
            output_file.write(json_line + '\n')
            image_count += 1
            label_count += len(image_data['annotations'])

    logging.info("Finished creating manifest file %s\nImages: %s\nLabels: %s",
                  manifest_file, image_count, label_count)

    return image_count, label_count

def add_arguments(parser):
    """
    Adds command line arguments to the parser.
    :param parser: The command line parser.
    """

    parser.add_argument(
        "--csv_file", help="The CSV file that you want to process.", required=True
    )

    parser.add_argument(
        "--s3_path", help="The S3 bucket and folder path for the images."
        " If not supplied, column 1 is assumed to include the S3 path.", required=False
    )

def main():

    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")

    try:

        # Get command line arguments
        parser = argparse.ArgumentParser(usage=argparse.SUPPRESS)
        add_arguments(parser)
        args = parser.parse_args()

        s3_path = args.s3_path
        if s3_path is None:
            s3_path = ''

        # Create file names.
        csv_file = args.csv_file
        file_name = os.path.splitext(csv_file)[0]
        manifest_file = f'{file_name}.manifest'
        duplicates_file = f'{file_name}-duplicates.csv'
        deduplicated_file = f'{file_name}-deduplicated.csv'

        # Create manifest file, if there are no duplicate rows.
        if check_duplicates(csv_file, deduplicated_file, duplicates_file):
            print(f"Duplicate rows found. Use {duplicates_file} to view duplicates "
                  f"and then update {deduplicated_file}. ")
            print(f"{deduplicated_file} contains the first occurrence of a duplicate row. "
                  "Update as necessary with the correct label information.")
            print(f"Re-run the script with {deduplicated_file}")
        else:
            print("No duplicate rows found. Creating manifest file.")

            image_count, label_count = create_manifest_file(csv_file,
                                                            manifest_file,
                                                            s3_path)

            print(f"Finished creating manifest file: {manifest_file} \n"
                  f"Images: {image_count}\nLabels: {label_count}")

    except FileNotFoundError as err:
        logging.exception("File not found: %s", err)
        print(f"File not found: {err}. Check your input CSV file.")

if __name__ == "__main__":
    main()
