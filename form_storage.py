import typing
from datetime import datetime

from pandas import DataFrame


class MatchAttribute:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value


class Form:
    def __init__(self, name: str, form_keyword_attribute: MatchAttribute, form_columns: [str], datetime_field: typing.Union[str, None]):
        self.name = name
        self.form_keyword_attribute = form_keyword_attribute
        self.form_columns = form_columns
        self.datetime_field = datetime_field
        self.data_frame: DataFrame = DataFrame(columns=self.get_form_columns())

    def get_form_columns(self):
        data_frame_columns = [form_column for form_column in self.form_columns]
        if self.datetime_field is not None:
            data_frame_columns = [self.datetime_field] + data_frame_columns
        return data_frame_columns


class FormStorage:
    def __init__(self, forms: [Form]):
        self.forms = forms

    def input_pattern_matches(self, matches: dict[str, str]):
        target_form: typing.Union[Form, None] = None
        for form in self.forms:
            if form.form_keyword_attribute.key in matches:
                match_value = matches[form.form_keyword_attribute.key]
                if form.form_keyword_attribute.value == match_value:
                    target_form = form
                    break

        new_data = {form_column: matches[form_column] for form_column in target_form.form_columns}

        if target_form.datetime_field is not None:
            new_data[target_form.datetime_field] = datetime.now().strftime('%y/%m/%d %H:%M:%S')

        target_form.data_frame.loc[len(target_form.data_frame)] = new_data
