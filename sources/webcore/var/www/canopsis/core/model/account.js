define([
	'jquery',
	'app/lib/ember',
	'app/lib/ember-data',
	'app/application'
], function($, Ember, DS, Application) {
	Application.Account = DS.Model.extend({
		id: DS.attr('number'),
		enable: DS.attr('boolean'),
		user: DS.attr('string'),
		firstname: DS.attr('string'),
		lastname: DS.attr('string'),
		mail: DS.attr('string'),
		aaa_group: DS.attr('string'),
		groups: DS.attr('array')
	});

	return Application.Account;
});