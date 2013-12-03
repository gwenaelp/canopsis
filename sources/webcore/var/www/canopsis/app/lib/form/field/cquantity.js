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

Ext.define('canopsis.lib.form.field.cquantity' , {
	extend: 'Ext.form.FieldContainer',
	mixins: ['canopsis.lib.form.cfield'],

	alias: 'widget.cquantity',

	layout: 'hbox',

	number_step: 1,
	number_min_val: 0,

	value: {unit: '%', value: 10},

	fieldLabel: undefined,

	initComponent: function() {
		
		this.logAuthor = '[' + this.id + ']';
		log.debug('Initialize ...', this.logAuthor);

		this.ts_value = Ext.widget('numberfield', {
			isFormField: false,
			name: 'value',
			width: 50,
			value:this.value.value,
			minValue: this.number_min_val,
			step: this.number_step
		});

		var store_data = [
			{name: _('%'), value: '%'},
			{name: _('Unit'), value: 'unit'},
			{name: _('Kilo'), value: 'kilo'},
			{name: _('Ton'), value: 'ton'},
			{name: _('Mega'), value: 'mega'},
			{name: _('Giga'), value: 'giga'},
			{name: _('Tera'), value: 'tera'}
		];

		this.ts_unit = Ext.widget('combobox', {
			isFormField: false,
			editable: false,
			width: 97,
			name: 'unit',
			queryMode: 'local',
			displayField: 'name',
			valueField: 'value',
			value: this.value.unit,
			fieldLabel: 'quantity'
			store: {
				xtype: 'store',
				fields: ['value', 'name'],
				data: store_data
			}
		});

		this.items = [this.ts_value, this.ts_unit];

		this.callParent(arguments);

		this.setValue(this.value);

	},

	checkDisable: function(combo, value) {
		void(combo);

		var disabled = value[0].raw.value? false : true;

		for (var i=0; i<items.length; i++) {
			var item = items[i];
			item.setDisabled(disabled);			
		}
	},

	show: function() {
		this.callParent(arguments);

		for (var i=0; i<items.length; i++) {
			var item = items[i];
			item.show();
			item.setDisabled(false);
		}
	},

	hide: function() {
		this.callParent(arguments);

		for (var i=0; i<items.length; i++) {
			var item = items[i];
			item.hide();
			item.setDisabled(true);
		}
	},

	getValue: function() {
		var result = {}

		for (var i=0; i<items.length; i++) {
			var item = items[i];
			result[item.getName()] = item.getValue();			
		}

		return result;
	},

	setValue: function(value) {
		if(value) {
			this.ts_value.setValue(value.value);
			this.ts_unit.setValue(value.unit);
		}
		else {
			this.setValue(this.value);
		}
	}
});
