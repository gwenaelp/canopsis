define([
	'jquery',
	'app/lib/ember',
	'app/application'
], function($, Ember, Application) {
	Application.SelectorsRoute = Ember.Route.extend({
		model: function() {
			var me = this;

			return $.ajax({
				url: '/rest/object/selector',
				type: 'GET',
				contentType: 'application/json'
			}).then(function(data, status, xhr) {
				var selectors = [];

				for(var i = 0; i < data.data.length; i++) {
					var selector = data.data[i];

					var pf_0 = selector.sla_timewindow_perfdata.findBy('metric', 'cps_pct_by_state_0');
					var pf_1 = selector.sla_timewindow_perfdata.findBy('metric', 'cps_pct_by_state_1');
					var pf_2 = selector.sla_timewindow_perfdata.findBy('metric', 'cps_pct_by_state_2');
					var pf_3 = selector.sla_timewindow_perfdata.findBy('metric', 'cps_pct_by_state_3');

					var account_prefix = 'account.';
					var group_prefix = 'group.';

					selectors.push({
						id: selector.id,
						rk: selector.rk,

						enable: selector.enable,
						loaded: selector.loaded,

						dostate: selector.dostate,
						dosla: selector.dosla,

						sla_state: selector.sla_state,
						sla_timewindow: selector.sla_timewindow,

						sla_pf_0: pf_0.value + pf_0.unit,
						sla_pf_1: pf_1.value + pf_1.unit,
						sla_pf_2: pf_2.value + pf_2.unit,
						sla_pf_3: pf_3.value + pf_3.unit,

						name: selector.crecord_name,
						display_name: selector.display_name,
						description: selector.description,
						owner: selector.aaa_owner.substring(account_prefix.length),
						group: selector.aaa_group.substring(group_prefix.length),
					});
				}

				/* return final model */
				var controller = me.controllerFor('selectors');

				return {
					'toolitems': controller.toolbar,
					'selectors': selectors
				};
			});
		}
	});

	Application.SelectorsController = Ember.ObjectController.extend({
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

			derogate: function(id) {
				;
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

	return Application.SelectorsController;
});