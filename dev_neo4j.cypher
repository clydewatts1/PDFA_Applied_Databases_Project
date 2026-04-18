MATCH(a:Attendee {AttendeeID: 133})-[:CONNECTED_TO]->(b:Attendee) RETURN a, b LIMIT 25;

MATCH(a:Attendee {AttendeeID:101} )-[:CONNECTED_TO]-(b:Attendee) RETURN a, b LIMIT 25;

//Try relationshipp

MATCH (a:Attendee{AttendeeID:103})-[:CONNECTED_TO]-(b:Attendee) RETURN a.,b;


MATCH (a:Attendee) RETURN a.AttendeeID