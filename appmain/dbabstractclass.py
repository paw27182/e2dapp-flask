from abc import ABC, ABCMeta, abstractmethod  # Abstract Base Class


class DBAbstractClass(metaclass=ABCMeta):
    def __init__(self, dbname, tablename):
        self.dbname = dbname
        self.tablename = tablename

    @abstractmethod
    def get_form_size(self, selected_form=None):
        """Find the number of form records

        Args:
            selected_form (str): the form table name

        Returns:
            int: the number of form records
        """
        return 0

    @abstractmethod
    def write_form_items(self, input_data):
        """Write form items into the table

        Args:
            input_data (list of list): the list of form items

        Returns:
            tuple of str: the return messages
        """
        return "OK", "Done."

    @abstractmethod
    def read_form_items(self, command):
        """Read form items from the table

        Args:
            command (str): command name, e.g.) 'show_the_first_item'

        Returns:
            tuple of lists: the list of table key names and the list of form items
        """
        return [], []  # key, items

    @abstractmethod
    def drop_form(self):
        """Delete the form table
        """
        pass

    @abstractmethod
    def delete_item(self, record_to_be_processed):
        """Delete the form record

        Args:
            record_to_be_processed (str): delete condition
        """
        pass
