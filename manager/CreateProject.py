#!/usr/bin/env python3
""" A script to create java project environments in the
path the script is run in, or a path specified by the user.

User can specify package names to create and can specify if template
'Main' files should be created for each package.
E.g: environment structure :

# -root_path
#     -build
#         -test
#             -classes
#             -reports
#     -doc
#     -lib
#     -src
#         -main
#             -groovy
#             -java
#                 -<package>
#                   -<package>.java
#         -test
#             -groovy
#             -java
#                 -<package> <- for testing
#                   -<package>.java <- for testing

Packages will be created from first dir under project dir. E.g:
src.test.java.<package>.<packageCLASS>
"""

import os
import sys
import json
import argparse


__author__ = "Brandon Bailey"
__copyright__ = "Copyright 2019, Brandon Bailey"
__credits__ = ["Brandon Bailey"]
__license__ = "GPL"
__version__ = "1.0.7"
__maintainer__ = "Brandon Bailey"
__email__ = ""
__status__ = "Production"


class PythonJavaProjectCreator(object):
    """class wrapper for java environment creator for library moduling"""

    def __init__(self):
        """initialize class"""

        pass

    def is_windows(self):
        """Function call to check if operating system is windows.
        :return: Boolean : true if win32"""

        if sys.platform == "win32":
            return True
        else:
            False

    def get_arguments(self):
        """function to return position arguments of
        project/ package creation
        :retrun: arguments: positional arguments"""

        parser = argparse.ArgumentParser()

        parser.add_argument("-n", "--new",
                            type=str,
                            help="new project")

        parser.add_argument("-p", "--packages",
                            nargs="+",
                            type=str,
                            help="if creating new package in project, \
                            package name")

        parser.add_argument("-f", "--files",
                            action='store_true',
                            help="create files")

        args = parser.parse_args()

        return args

    def validate_root_location(self):
        """sanity check function to confirm that current working directory
        is desired directory for project creation. If not,
        allow user to specify path and store it.
        :return: working_directory: path to project"""

        desired_path = os.getcwd()

        is_correct_path = input(f"Java project will be created in : \
                                {desired_path} is this correct? [y/n/q] ")

        if is_correct_path.lower() == "y":
            print(f"Creating project in path : {desired_path}")

        if is_correct_path.lower() == "n":
            desired_path = input("Please specify the desired path : ")

        if is_correct_path.lower() == "q":
            sys.exit(1)

        if not os.path.exists(desired_path):
            print("Warning: Specified path does not exist. Will attempt to create.")

            try:
                os.mkdir(desired_path)

            except Exception as error:
                print(f"Warning : Error creating directory : {error}")

        return desired_path

    def json_template_check(self, root_path):
        """function to determine and retrieve json file data
        for directory template.
        :param: root_path : path to root location either specified by user
        or based on CWD
        :return: json_data_template"""

        files_in_dir = os.listdir(root_path)
        print(files_in_dir)

        if not files_in_dir:
            print("Warning: No files found, Using default.")
            return None

        try:
            json_file = [os.path.join(root_path, f) for f in files_in_dir \
                         if "template_paths" in f and f.endswith(".json")][0]

        except Exception as error:
            print(f"Warning : No json templates found in destionation : {error}")
            return None

        print("Found json template. retrieving data.")

        with open(json_file, "r") as handle:
            raw_data = json.load(handle)

        return raw_data

    def create_directory_streams(self, project_root, template):
        """goes through and creates directory tree based on template.
        :param: project_root : root path location for project
        :param: template : specific template for dirs to follow"""

        java_paths = set()
        for directory in template:
            model = os.path.join(project_root, directory)

            if os.path.basename(model) == "java":
                java_paths.add(model)

            if not os.path.exists(model):
                try:
                    os.makedirs(model)
                except Exception as error:
                    print(f"Warning: error creating project directory : {error}")
            else:
                print(f"Path exists : {model}")

        return java_paths

    def create_package_template_file(self, project_root, model, package):
        """function to create template java file to behave as package main.
        :param: project_root : root of project path
        :param: model : current java model (src/main/; src/test etc.)
        :param: package : current package working on"""

        # get project name from root
        project = os.path.basename(project_root)

        # replace slashes with periods for package parsing
        if self.is_windows():
            package_header = '.'.join(model.split(project, 1)[1].split("\\")[1:])
        else:
            package_header = '.'.join(model.split(project, 1)[1].split("/")[1:])

        # java file template text structure
        file_text = f"""
package {package_header};

public class {package} {{

    public static void main(String[] args) {{

        System.out.println("Package :\\n\\t{package}\\nFrom :\\n\\t{package_header}\\nCreated successfully.");

    }}

}}

    """
        # full file path
        template_file = os.path.join(model, f"{package}.java")

        # create/open file and write template to it
        with open(template_file, "w+") as file_handle:
            file_handle.write(file_text)

    def create_packages(self, project_root, package_roots, packages, make_files=False):
        """function to create package directories if packages specified
        :param: package_roots : set of java folder paths"""

        for path in package_roots:
            for package_name in packages:
                model = os.path.join(path, package_name)

                if not os.path.exists(model):

                    try:
                        os.mkdir(model)
                    except Exception as error:
                        print(f"Warning: error creating package folders : {error}")

                if make_files:
                    self.create_package_template_file(project_root, model, package_name)

    def create_environment(self):
        """main class loop for environment creation"""

        args = self.get_arguments()

        root_path = self.validate_root_location()

        json_template = self.json_template_check(root_path)

        if json_template or json_template != None:
            template = [json_template[key] for key in json_template][0]

        else:
            template = ["build/test/classes",
                        "build/test/reports",
                        "doc",
                        "lib",
                        "src/main/groovy",
                        "src/main/java",
                        "src/test/groovy",
                        "src/test/java"]

        if self.is_windows():
            template = [template_path.replace("/","\\") for template_path in template]

        if args.new:
            print(f"new project : {args.new}")

            project_root = os.path.join(root_path, args.new)

            if not os.path.exists(project_root):
                os.mkdir(project_root)

        else:
            project_root = os.getcwd()

        package_roots = self.create_directory_streams(project_root, template)

        if args.packages:
            print(f"package names : {[i for i in args.packages]}")

            if args.files:
                print("Will create package files")
                self.create_packages(project_root, package_roots, args.packages,
                                    make_files = args.files)

            else:
                self.create_packages(project_root, package_roots, args.packages)


if __name__ == '__main__':

    PythonJavaProjectCreator().create_environment()
