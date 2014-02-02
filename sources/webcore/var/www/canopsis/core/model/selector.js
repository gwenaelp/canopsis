define([
	'jquery',
	'app/lib/ember',
	'app/lib/ember-data',
	'app/application'
], function($, Ember, DS, Application) {
	Application.Selector = DS.Model.extend({
		rk: DS.attr('string'),
		enable: DS.attr('boolean'),
		loaded: DS.attr('boolean'),
		dostate: DS.attr('boolean'),
		dosla: DS.attr('boolean'),
		sla_state: DS.attr('number'),
		sla_timewindow: DS.attr('number'),
		sla_pf_0: DS.attr('string'),
		sla_pf_1: DS.attr('string'),
		sla_pf_2: DS.attr('string'),
		sla_pf_3: DS.attr('string'),
		name: DS.attr('string'),
		display_name: DS.attr('string'),
		description: DS.attr('string'),
		owner: DS.attr('string'),
		group: DS.attr('string')
	});

	Application.Selector.reopenClass({
		findAll: function(store, authkey) {
			return $.ajax({
				url: '/rest/object/selector',
				method: 'GET',
				contentType: 'application/json',
				data: {
					authkey: authkey
				}
			});
		},

		extractFindAll: function(store, payload) {
			var selectors = [];

			for(var i = 0; i < payload.data.length; i++) {
				var selector = payload.data[i];

				var pf_0 = selector.sla_timewindow_perfdata.findBy('metric', 'cps_pct_by_state_0');
				var pf_1 = selector.sla_timewindow_perfdata.findBy('metric', 'cps_pct_by_state_1');
				var pf_2 = selector.sla_timewindow_perfdata.findBy('metric', 'cps_pct_by_state_2');
				var pf_3 = selector.sla_timewindow_perfdata.findBy('metric', 'cps_pct_by_state_3');

				selector.sla_pf_0 = pf_0.value + pf_0.unit;
				selector.sla_pf_1 = pf_1.value + pf_1.unit;
				selector.sla_pf_2 = pf_2.value + pf_2.unit;
				selector.sla_pf_3 = pf_3.value + pf_3.unit;

				selector.name = selector.crecord_name;

				selector.owner = selector.aaa_owner.substring('account.'.length);
				delete selector.aaa_owner;

				selector.group = selector.aaa_group.substring('group.'.length);
				delete selector.aaa_group;

				selectors.push(selector);
			}

			return selectors;
		}
	});

	return Application.Selector;
});