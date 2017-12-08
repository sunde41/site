#!/usr/bin/perl -pi
s/\{% trans "([^"]+)" %\}/\{\{ _\('$1'\) \}\}/g;
s/if  +/if /g;
s/\{% *static "([^"]+)" *%\}/{{ static('$1') }}/g;
s/\{% *url "([^"]+)" *%\}/{{ url('$1') }}/g;
s/\.jade"/\.html"/g;
s/\|escape//g;
s/\{% url "([^"]+)" (\S+) *%\}/{{ url('$1', $2) }}/;
s/\{% url "([^"]+)" (\S+) +(\S+) *%\}/{{ url('$1', $2, $3) }}/;
s/\{% url "([^"]+)" (\S+) +(\S+) +(\S+) *%\}/{{ url('$1', $2, $3, $4) }}/;
s/\{% url "([^"]+)" (\S+) +(\S+) +(\S+) +(\S+) *%\}/{{ url('$1', $2, $3, $4, $5) }}/;
s:/>:>:g;
s/non_field_errors(?!\()/non_field_errors()/g;
s/as_table(?!\()/as_table()/g;
s/as_ul(?!\()/as_ul()/g;
s/as_p(?!\()/as_p()/g;
