define(function(require, exports, module) {
	var Application = require('app/application');

	Application.ApplicationRoute = Ember.Route.extend({
		model: function() {
			return {
				title: 'Canopsis',
				menu: [{
					name: 'Build',
					icon: 'cog',
					links: [
						{url: '/build/accounts', title: 'Accounts', icon: 'user'},
						{url: '/build/groups', title: 'Groups', icon: 'book'},
						{url: '/build/curves', title: 'Curves', icon: 'picture'},
						{url: '/build/perfdata', title: 'PerfData', icon: 'stats'},
						{url: '/build/selectors', title: 'Selectors', icon: 'link'},
						{url: '/build/consolidation', title: 'Consolidation', icon: 'compressed'},
						{url: '/build/topologies', title: 'Topologies', icon: 'tree-conifer'},
						{url: '/build/eventfilter', title: 'Filter Rules', icon: 'filter'}
					]
				},{
					name: 'Run',
					icon: 'play',
					links: [
						{url: '/run/dashboard', title: 'Dashboard', icon: 'dashboard'}
					]
				}]
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