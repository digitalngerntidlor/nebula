from datetime import datetime

from datetime import datetime, timedelta

def generate_start_end_date(start: str = None, end: str = None, interval: int = None) -> tuple[str, str]:
    """
    Generates a start and end date string based on the provided arguments.
    
    - If start and end are both provided, it validates and returns them.
    - If an interval (in days) is provided, it calculates a range relative to today.
    """
    # Standard format for input/output string dates
    date_format = "%Y-%m-%d"
    today = datetime.today()

    # Case 1: Both start and end dates are provided
    if start and end:
        # We parse them just to ensure they are valid date formats
        try:
            datetime.strptime(start, date_format)
            datetime.strptime(end, date_format)
        except ValueError:
            raise ValueError(f"Dates must be in {date_format} format")
        return start, end

    # Case 2: Only an interval (in days) is provided
    elif interval is not None:
        # If interval is positive, treat today as start. If negative, treat today as end.
        if interval >= 0:
            start_dt = today
            end_dt = today + timedelta(days=interval)
        else:
            start_dt = today + timedelta(days=interval)
            end_dt = today
            
        return start_dt.strftime(date_format), end_dt.strftime(date_format)

    # Case 3: Edge case where neither or insufficient arguments are passed
    else:
        raise ValueError("Must provide either both 'start' and 'end', or an 'interval'")
    