define(function(require, exports, module) {
	var Canopsis = Ember.Application.create();

	Canopsis.Router.map(function() {
		this.resource('canopsis', { path: '/' });
	});

	return Canopsis;
});