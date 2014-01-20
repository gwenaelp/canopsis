define(function(require, exports, module) {
	Ember.Handlebars.helper('glyphicon', function(icon) {
		return new Ember.Handlebars.SafeString('<span class="glyphicon glyphicon-' + icon + '"></span>');
	});
});