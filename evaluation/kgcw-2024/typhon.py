#!/usr/bin/env python3

"""
The MappingTemplate executes RML rules to generate high quality Linked Data
from multiple originally (semi-)structured data sources.

**Website**: https://rml.io<br>
**Repository**: https://github.com/RMLio/rmlmapper-java
"""

import os
import psutil
import time
from typing import Optional
from timeout_decorator import timeout, TimeoutError  # type: ignore
from bench_executor.logger import Logger
from bench_executor.container import Container

TIMEOUT = 5  # 5 min

class MappingTemplate(Container):
    """MappingTemplate container for executing MTL mappings."""

    def __init__(self, data_path: str, config_path: str, directory: str,
                 verbose: bool, expect_failure: bool = False):
        """Creates an instance of the MappingTemplate class.

        Parameters
        ----------
        data_path : str
            Path to the data directory of the case.
        config_path : str
            Path to the config directory of the case.
        directory : str
            Path to the directory to store logs.
        verbose : bool
            Enable verbose logs.
        expect_failure : bool
            If a failure is expected, default False.
        """
        self._data_path = os.path.abspath(data_path)
        self._config_path = os.path.abspath(config_path)
        self._logger = Logger(__name__, directory, verbose)
        self._verbose = verbose

        os.makedirs(os.path.join(self._data_path, 'typhon-rml'), exist_ok=True)
        super().__init__(f'cefriel/typhon-rml:latest', 'MappingTemplate',
                         self._logger, expect_failure=expect_failure,
                         volumes=[
                             # f'{self._data_path}/typhon-rml:/app/data',
                                  f'{self._data_path}/shared:/app/data'])

    @property
    def root_mount_directory(self) -> str:
        """Subdirectory in the root directory of the case for MappingTemplate.

        Returns
        -------
        subdirectory : str
            Subdirectory of the root directory for MappingTemplate.

        """
        return __name__.lower()

    @timeout(TIMEOUT)
    def _execute_with_timeout(self, arguments: list) -> bool:
        """Execute a mapping with a provided timeout.

        Returns
        -------
        success : bool
            Whether the execution was successfull or not.
        """
        # FIXME this is something that is necessary for the RMLmapper, do we also need it?

        # Set Java heap to 1/2 of available memory instead of the default 1/4
        max_heap = int(psutil.virtual_memory().total * (1/2))

        # FIXME this is something that is necessary for the RMLmapper, do we also need it?
        # Execute command
        # cmd = f'java -Xmx{max_heap} -Xms{max_heap}' + \

        typhon_cmd = 'java -jar /app/typhon-rml.jar --rml-mapping ./data/mapping.ttl'
        # can see them outside of the container in the data/shared folder
        create_dir_cmd = 'mkdir -p /app/data/data'
        copy_files_cmd = 'mv /app/route.xml /app/data/data && mv /app/template.vm /app/data/data && mv /app/chimera-typhon-skeleton.jar /app/data'
        route_exec__cmd = "cd /app/data && java -jar chimera-typhon-skeleton.jar"

        cmd = f'{typhon_cmd} && {create_dir_cmd} && {copy_files_cmd} && {route_exec__cmd}'
        # && {route_exec__cmd}
        return self.run_and_wait_for_exit(cmd)

    def execute(self, arguments: list) -> bool:
        """Execute MappingTemplate with given arguments.

        Parameters
        ----------
        arguments : list
            Arguments to supply to MappingTemplate.

        Returns
        -------
        success : bool
            Whether the execution succeeded or not.
        """
        try:
            return self._execute_with_timeout(arguments)
        except TimeoutError:
            msg = f'Timeout ({TIMEOUT}s) reached for MappingTemplate'
            self._logger.warning(msg)

        return False

    def execute_mapping(self,
                        mapping_file: str,
                        output_file: str,
                        input_format: Optional[str] = None,
                        serialization: Optional[str] = None,
                        input_file: Optional[str] = None,
                        output_formatter: Optional[str] = None,
                        rdb_username: Optional[str] = None,
                        rdb_password: Optional[str] = None,
                        rdb_host: Optional[str] = None,
                        rdb_port: Optional[int] = None,
                        rdb_name: Optional[str] = None) -> bool:
        """Execute a mapping file with MappingTemplate.

        Parameters
        ----------
        input_file : Optional[str]
            File used as input for a mapping.
        mapping_file : str
            Path to the mapping file to execute.
        output_file : str
            Name of the output file to store the triples in.
        formatter : str
            Formatter format to use.
        rdb_username : Optional[str]
            Username for the database, required when a database is used as
            source.
        rdb_password : Optional[str]
            Password for the database, required when a database is used as
            source.
        rdb_host : Optional[str]
            Hostname for the database, required when a database is used as
            source.
        rdb_port : Optional[int]
            Port for the database, required when a database is used as source.
        rdb_name : Optional[str]
            Database name for the database, required when a database is used as
            source.
        Returns
        -------
        success : bool
            Whether the execution was successfull or not.
        """
        arguments = [os.path.join('/data/shared/', mapping_file),
                     os.path.join('/data/shared/', output_file)]

        return self.execute(arguments)

