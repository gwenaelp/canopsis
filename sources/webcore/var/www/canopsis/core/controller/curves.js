define([
	'jquery',
	'app/lib/ember',
	'app/application'
], function($, Ember, Application) {
	Application.CurvesRoute = Ember.Route.extend({
		model: function() {
			var me = this;

			return $.ajax({
				url: '/rest/object/curve',
				method: 'GET',
				contentType: 'application/json'
			}).then(function(data, status, xhr) {
				var curves = [];

				for(var i = 0; i < data.data.length; i++) {
					var curve = data.data[i];

					curves.push({
						line_color: '#' + curve.line_color,
						area_color: '#' + curve.area_color,
						line_style: curve.dashStyle,
						area_opacity: curve.area_opacity,
						zindex: curve.zIndex,
						invert: curve.invert,
						metric: curve.metric,
						label: curve.label
					});
				}

				/* return final model */
				var controller = me.controllerFor('curves');

				return {
					'toolitems': controller.toolbar,
					'curves': curves
				};
			});
		}
	});

	Application.CurvesController = Ember.ObjectController.extend({
		toolbar: [{
			title: 'Refresh',
			action: 'refresh',
			icon: 'refresh'
		},{
			title: 'Add',
			action: 'add',
			icon: 'plus-sign'
		},{
			title: 'Duplicate',
			action: 'duplicate',
			icon: 'file'
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

			duplicate: function() {
				;
			},

			remove: function() {
				;
			}
		}
	});

	return Application.CurvesController;
});