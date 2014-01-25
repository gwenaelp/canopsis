define([
	'jquery',
	'app/lib/ember',
	'app/application'
], function($, Ember, Application) {
	Application.PerfdataRoute = Ember.Route.extend({
		model: function() {
			var me = this;

			return $.ajax({
				url: '/perfstore',
				type: 'GET',
				contentType: 'application/json'
			}).then(function(data, status, xhr) {
				var controller = me.controllerFor('perfdata');

				return {
					'toolitems': controller.toolbar,
					'perfdatas': data.data
				};
			});
		}
	});

	Application.PerfdataController = Ember.ObjectController.extend({
		toolbar: [{
			title: 'Refresh',
			action: 'refresh',
			icon: 'refresh'
		},{
			title: 'Remove',
			action: 'remove',
			icon: 'trash'
		}],

		actions: {
			do: function(action) {
				this.send(action);
			},

			refresh: function() {
				;
			},

			remove: function() {
				;
			}
		}
	});
});