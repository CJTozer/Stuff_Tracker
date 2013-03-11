def time_string(time_in_mins):
    # Make sure we have an int
    time_in_mins = int(time_in_mins)
    # >= 1h - print e.g. "2 1/4 hours"
    if time_in_mins > 60:
        hour_part = time_in_mins / 60
        min_part = time_in_mins % 60
        frac_part = ""
        if min_part >= 45:
            frac_part = " &frac34;"
        elif min_part >= 30:
            frac_part = " &frac12;"
        elif min_part >= 15:
            frac_part = " &frac14;"
        return "%d%s hours" % (hour_part, frac_part)
    # Just a handful of minutes
    elif time_in_mins > 0:
        return "%d minutes" % time_in_mins
    # No time
    else:
        return "No time spent yet"
    
        