# SBOL Validator worker class
# Written by Zach Zundel
# zach.zundel@utah.edu
# 08/13/2016
# Imported from https://github.com/SynBioDex/SBOL-Validator
import subprocess
import tempfile
import uuid
import traceback
import os

from sbol2 import Config, ConfigOptions


class ValidationResult:
    def __init__(self, output_file, equality):
        self.check_equality = equality
        self.output_file = output_file
        self.valid = False
        self.errors = []

    def digest_errors(self, output):
        self.errors = output.strip().split('\n')

    def decipher(self, output, options):
        if self.check_equality:
            if "differ" in output or "not found in" in output:
                self.equal = False
            else:
                self.equal = True

        if "Validation successful, no errors." not in output:
            self.valid = False
            self.digest_errors(output)
        else:
            self.digest_errors(output.strip(u"Validation successful, no errors."))
            self.valid = True

            if options.return_file:
                with open(options.output_file, 'r') as file:
                    self.result = file.read()

    def broken_validation_request(self, command):
        self.valid = False
        self.errors = ["Something about your validation request is contradictory or poorly-formed!", " ".join(command)]

    def json(self):
        return self.__dict__


class ValidationRun:
    def __init__(self, options, validation_file, diff_file=None):
        self.options = options
        self.validation_file = validation_file
        self.diff_file = diff_file

    def execute(self):
        result = ValidationResult(self.options.output_file, self.options.test_equality)

        # Attempt to run command
        jar_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "libSBOLj.jar")
        command = self.options.command(jar_path, self.validation_file, self.diff_file)
        try:
            output = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.STDOUT)
            result.decipher(output, self.options)
        except subprocess.CalledProcessError as exception:
            # If the command fails, the file is not valid.
            result.valid = False
            result.errors += [exception.output, ]
        except ValueError as ve:
            print(traceback.print_tb(ve.__traceback__))
            result.broken_validation_request(command)

        return result.json()


class ValidationOptions:
    language = "SBOL2"
    subset_uri = False
    fail_on_first_error = False
    provide_detailed_stack_trace = False
    check_uri_compliance = True
    check_completeness = True
    check_best_practices = False
    uri_prefix = False
    version = False
    insert_type = False
    test_equality = False
    return_file = True
    main_file_name = "main file"
    diff_file_name = "comparison file"

    def __init__(self, return_file):
        self.return_file = return_file

    def build(self, work_dir, data):
        for key, value in data.items():
            setattr(self, key, value)
        self.output_file = os.path.join(work_dir, str(uuid.uuid4()))

        if self.language in ['SBOL1', 'SBOL2', 'SBML']:
            self.output_file = self.output_file + ".rdf"
        elif self.language == 'GFF3':
            self.output_file = self.output_file + '.gff'
        elif self.language == 'GenBank':
            self.output_file = self.output_file + '.gb'
        else:
            self.output_file = self.output_file + '.fasta'

    def command(self, jar_path, validation_file, diff_file=None):
        java_location = Config.getOption(ConfigOptions.JAVA_LOCATION)
        command = [java_location, "-jar", jar_path, validation_file, "-o", self.output_file, "-l", self.language]

        if self.test_equality and diff_file:
            command += ["-e", diff_file, "-mf", self.main_file_name, "-cf", self.diff_file_name]
        elif self.test_equality and not diff_file:
            raise ValueError

        if self.subset_uri:
            command += ["-s", self.subset_uri]

        if self.provide_detailed_stack_trace and not self.fail_on_first_error:
            raise ValueError

        if self.fail_on_first_error:
            command += ["-f"]

        if self.provide_detailed_stack_trace:
            command += ["-d"]

        if not self.check_uri_compliance:
            command += ["-n"]

        if not self.check_completeness:
            command += ["-i"]

        if self.check_best_practices:
            command += ["-b"]

        if self.uri_prefix:
            command += ["-p", self.uri_prefix]

        if self.version:
            command += ["-v", self.version]

        if self.insert_type:
            command += ["-t"]

        return command


def do_validation(json):
    """
    Performs validation based on a json request
    """
    with tempfile.TemporaryDirectory() as work_dir:
        options = ValidationOptions(json['return_file'])
        options.build(work_dir, json['options'])

        main_filename = os.path.join(work_dir, str(uuid.uuid4()) + ".sbol")
        with open(main_filename, 'a+') as file:
            file.write(json["main_file"])

        if json['options']['test_equality']:
            diff_filename = os.path.join(work_dir, str(uuid.uuid4()) + ".sbol")

            with open(diff_filename, 'a+') as file:
                file.write(json["diff_file"])

            run = ValidationRun(options, main_filename, diff_filename)
        else:
            run = ValidationRun(options, main_filename)

        result = run.execute()
        return result
