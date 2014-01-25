define([
	'jquery',
	'app/lib/ember',
	'app/application'
], function($, Ember, Application) {
	Application.ConsolidationRoute = Ember.Route.extend({
		model: function() {
			var me = this;

			return $.ajax({
				url: '/rest/object/consolidation',
				type: 'GET',
				contentType: 'application/json'
			}).then(function(data, status, xhr) {
				var consolidations = [];

				for(var i = 0; i < data.data.length; i++) {
					var conso = data.data[i];

					consolidations.push({
						id: conso.id,

						loaded: conso.loaded,
						enable: conso.enable,

						name: conso.crecord_name,
						component: conso.component,
						resource: conso.resource,

						aggregation_interval: conso.aggregation_interval,
						aggregation_method: conso.aggregation_method,
						consolidation_method: conso.consolidation_method,

						message: conso.output_engine,
						nb_items: conso.nb_items
					});
				}

				/* return final model */
				var controller = me.controllerFor('consolidation');

				return {
					'toolitems': controller.toolbar,
					'consolidations': consolidations
				};
			});
		}
	});

	Application.ConsolidationController = Ember.ObjectController.extend({
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
		},{
			title: 'Import',
			action: 'import',
			icon: 'import'
		},{
			title: 'Export',
			action: 'export',
			icon: 'open'
		}],

		actions: {
			do: function(action) {
				this.send(action);
			},

			refresh: function() {
				;
			},

			add: function() {
				;
			},

			duplicate: function() {
				;
			},

			remove: function() {
				;
			},

			import: function() {
				;
			},

			export: function() {
				;
			}
		}
	});
});