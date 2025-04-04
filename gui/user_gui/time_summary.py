from datetime import timedelta

class TimeSummary:
    @staticmethod
    def parse_time_string(tstr):
        try:
            parts = tstr.split(":")
            if len(parts) == 2:
                return timedelta(hours=int(parts[0]), minutes=int(parts[1]))
            elif len(parts) == 3:
                return timedelta(hours=int(parts[0]), minutes=int(parts[1]), seconds=int(parts[2]))
        except:
            return timedelta()
        return timedelta()

    @staticmethod
    def summarize(data):
        total_active = timedelta()
        total_inactive = timedelta()

        for row in data:
            active      = TimeSummary.parse_time_string(row[1])
            inactive    = TimeSummary.parse_time_string(row[2])

            total_active += active
            total_inactive += inactive

        total = total_active + total_inactive

        return {
            "active": TimeSummary.format_td(total_active),
            "inactive": TimeSummary.format_td(total_inactive),
            "total": TimeSummary.format_td(total)
        }

    @staticmethod
    def format_td(td):
        total_minutes = int(td.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}h {minutes}m"
