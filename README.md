# Web_Calendar
You can add event to the calendar using POST method, passing "event" (str format) and "date" (YYYY-MM-DD format) as arguments "/event",
Get full list of events "/event",
Get one particular event "/event/<int:id>",
Get list of events in some time interval, passing "start_dime" (YYYY-MM-DD format) and "end_time" (YYYY-MM-DD format) as arguments "/event",
Remove events from calendar "/event/<int:id>".
