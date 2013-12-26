/*
# Copyright (c) 2013 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
*/

Ext.define('canopsis.lib.form.field.cforecast' , {
	extend: 'Ext.form.FieldContainer',
	mixins: ['canopsis.lib.form.cfield'],

	alias: 'widget.cforecast',

	layout: 'vbox',

	fieldLabel: undefined,

	Custom: {category: "Custom", demand: 0, beta: 0, trend: 0},
	NotLinearMidVariable: {category:"Not linear mid variable", demand:0.99, beta:0.12, trend:0.80},
	LinearNotVariable: {category:"Linear not variable", demand:0.99, seasonality:0.01, trend:0.97},
	NotLinearVariable: {category:"Not linear variable", demand:0.60, seasonality:1, trend:0.01},
	LinearVariable: {category:"Linear variable", demand:0.68, seasonality:0.01, trend:0.17},
	BestEffort: {category: "BestEffort", demand: 0, beta: 0, trend: 0},

	defaultCategory: NotLinearMidVariable,

	value: {
		enable: false,
		max_points: 250,
		duration: {value: 0, unit: 'day'},
		enddate: undefined,
		category: this.Custom,
		demand: this.defaultCategory.demand,
		seasonality: this.defaultCategory.seasonality,
		trend: this.defaultCategory.trend,
		threshold: {value: 10, unit: '%'}
	},

	initComponent: function() {
		this.logAuthor = '[' + this.id + ']';
		log.debug('Initialize ...', this.logAuthor);

		this.ts_enable = Ext.widget('checkbox', {
			name: 'enable',
			checked: this.value.enable,
			labelField: 'Enable',
			listeners: {
				changed: {
					if (this.ts_enable.getValue()) {
						for (var index=0; index<this.ts_items.length; index++) {
							item = this.ts_items[index];
							if (item !== this.ts_enable) {
								item.disable();
								item.hide();
							}
						}
					} else {
						for (var index=0; index<this.ts_items.length; index++) {
							item = this.ts_items[index];
							if (item !== this.ts_enable) {
								item.enable();
								item.show();
							}
						}
					}
				}
			}
		});
		this.ts_max_points = Ext.widget('numberfield', {
			name: 'max_points',
			width: 50,
			value: this.value.max_points,
			minValue: this.max_points_min,
			labelField: 'Max points'
		});
		this.ts_duration = Ext.widget('cperiod', {
			isFormField: false,
			name: 'duration',
			value:this.value.duration,
			minValue: this.number_min_val,
			fieldLabel: 'Duration (if no max points)'
		});
		this.ts_enddate = Ext.widget('datefield', {
			name: 'enddate',
			value: this.value.enddate,
			fieldLabel: 'End date (if no max points and no duration',
		});

		var category_store_data [
			{'name': _(this.NotLinearMidVariable.category), 'value': this.NotLinearMidVariable},
			{'name': _(this.LinearNotVariable.category), 'value': this.LinearNotVariable},
			{'name': _(this.LinearVariable.category), 'value': this.LinearVariable},
			{'name': _(this.LinearVariable.category), 'value': this.LinearVariable},
			{'name': _(this.Custom.category), 'value': this.Custom},
		];

		// algorithm parametes
		this.ts_category = Ext.widget('combobox', {
			isFormField: false,
			editable: false,
			width: 97,
			name: 'category',
			queryMode: 'local',
			displayField: 'name',
			valueField: 'value',
			labelField: 'Category',
			store: {
				xtype: 'store',
				fields: ['value', 'name'],
				data: category_store_data
			}
		});
		this.ts_demand = Ext.widget('numberfield', {
			name: 'demand',
			value: this.value.demand,
			fieldLabel: 'Demand (alpha)'
		});
		this.ts_seasonality = Ext.widget('numberfield', {
			name: 'seasonality',
			value: this.value.seasonality,
			fieldLabel: 'Seasonality (beta)'
		});
		this.ts_trend = Ext.widget('numberfield', {
			name: 'trend',
			value: this.value.trend,
			fieldLabel: 'Trend (gamma)'
		});
		this.ts_threshold = Ext.widget('cthreshold', {
			name: 'threshold',
			value: this.value.threshold,
			fieldLabel: 'Forecast threshold'
		});
		this.items = [
			this.ts_enable,
			this.ts_max_points,
			this.ts_duration,
			this.ts_enddate,
			this.ts_category,
			this.ts_demand,
			this.ts_seasonality,
			this.ts_trend,
			this.ts_threshold,
		];

		this.callParent(arguments);

		this.setValue(this.value);

	},

	checkDisable: function(combo, value) {
		void(combo);

		this.callParent(arguments);

		var disabled = value[0].raw.value;

		for (var i=0; i<this.items.length; i++) {
			var item = this.items[i];
			item.setDisabled(disabled);
		}
	},

	show: function() {
		this.callParent(arguments);
		for (int i=1; i<this.items.length; i++) {
			item = this.items[i];
			item.show();
			item.setDisabled(false);
		};
	},

	hide: function() {
		this.callParent(arguments);
		for (int i=1; i<this.items.length; i++) {
			item = this.items[i];
			item.hide();
			item.setDisabled(true);
		};
	},

	getValue: function() {
		result = {};

		for (int i=0; i<this.items.length; i++) {
			item = this.items[i];
			result[item.getName()] = item.getValue();
		};

		return result;
	},

	setValue: function(value) {
		if(value) {
			for (int i=0; i<this.items.length; i++) {
				item = this.items[i];
				item.setValue(value[item.getName()]);
			}
		} else {
			this.setValue(this.value);
		}
	}
});
