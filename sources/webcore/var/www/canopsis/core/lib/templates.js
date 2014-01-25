var templates = [
	'application',
	'accounts',
	'groups',
	'curves',
	'perfdata',
	'selectors',
	'consolidation'
];

var deps = ['app/lib/ember'];

for(var i = 0; i < templates.length; i++) {
	deps.push('text!app/templates/' + templates[i] + '.html');
}

define(deps, function(Ember) {
	for(var i = 1; i < arguments.length; i++) {
		Ember.TEMPLATES[templates[i - 1]] = Ember.Handlebars.compile(arguments[i]);
	}
});