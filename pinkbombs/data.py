import pandas as pd

def calculate_tonnage_difference(input_df, input_year):
    selected_year_data = input_df[input_df['Year'] == input_year].reset_index()
    previous_year_data = input_df[input_df['Year'] == input_year - 1].reset_index()
    selected_year_data['tonnage_difference'] = selected_year_data["Tonnes - live weight"].sub(previous_year_data["Tonnes - live weight"], fill_value=0)
    return pd.concat([selected_year_data["Country Name En"], selected_year_data["Tonnes - live weight"], selected_year_data.tonnage_difference], axis=1).sort_values(by="tonnage_difference", ascending=False)

def format_number(num):
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'
