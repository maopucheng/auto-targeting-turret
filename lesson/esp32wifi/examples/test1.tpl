{% args var, another %}
hello
first arg: {{var}}
second arg: {{another}}
{% for i in range(5) %}
{% if i % 2 %}
world
{% elif i % 3 == 0 %}
something else
{% else %}
skies
{% endif %}
text{{i + 10}}
{% endfor %}
trailer
