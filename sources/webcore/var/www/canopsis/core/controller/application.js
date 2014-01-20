define(function(require, exports, module) {
	var Application = require('app/application');

	Application.ApplicationRoute = Ember.Route.extend({
		model: function() {
			return {
				title: 'Canopsis',
				menu: [
					{
						name: 'Build',
						icon: 'cog',
						links: [
							{url: '/build/accounts', title: 'Accounts', icon: 'user'},
							{url: '/build/groups', title: 'Groups'},
							{url: '/build/curves', title: 'Curves'},
							{url: '/build/perfdata', title: 'PerfData'}
						]
					},
					{
						name: 'Run',
						icon: 'play',
						links: [
							{url: '/run/dashboard', title: 'Dashboard', icon: 'dashboard'}
						]
					}
				]
			};
		}
	});

	Application.ApplicationController = Ember.ObjectController.extend({
		actions: {
			openTab: function(url) {
				this.transitionToRoute(url);
			}
		}
	});
});