#This customization was done by Elvis Ndegwa Knagethe
#for any explanation reach out to elvisndegwa9
from __future__ import unicode_literals

from erpnext.manufacturing.doctype.bom.bom import BOM
import json


import frappe
from frappe import ValidationError, _, scrub, throw
from frappe.utils import cint, comma_or, flt, getdate, nowdate
from six import iteritems, string_types
from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
from frappe.utils import (
	add_days,
	ceil,
	cint,
	comma_and,
	flt,
	get_link_to_form,
	getdate,
	now_datetime,
	nowdate,
)




def get_child_exploded_items(self, bom_no, stock_qty):
	""" Add all items from Flat BOM of child BOM"""
	# Did not use qty_consumed_per_unit in the query, as it leads to rounding loss
	child_fb_items = frappe.db.sql("""
		SELECT
			bom_item.item_code,
			bom_item.item_name,
			bom_item.description,
			bom_item.source_warehouse,
			bom_item.operation,
			bom_item.stock_uom,
			bom_item.stock_qty,
			bom_item.rate,
			bom_item.include_item_in_manufacturing,
			bom_item.sourced_by_supplier,
			bom_item.main_item,
			bom_item.stock_qty / ifnull(bom.quantity, 1) AS qty_consumed_per_unit
		FROM `tabBOM Explosion Item` bom_item, tabBOM bom
		WHERE
			bom_item.parent = bom.name
			AND bom.name = %s
			AND bom.docstatus = 1
	""", bom_no, as_dict = 1)

	for d in child_fb_items:
		self.add_to_cur_exploded_items(frappe._dict({
			'item_code'				: d['item_code'],
			'item_name'				: d['item_name'],
			'source_warehouse'		: d['source_warehouse'],
			'operation'				: d['operation'],
			'description'			: d['description'],
			'stock_uom'				: d['stock_uom'],
			'stock_qty'				: d['qty_consumed_per_unit'] * stock_qty,
			'rate'					: flt(d['rate']),
			'main_item'					: d['main_item'],
			'include_item_in_manufacturing': d.get('include_item_in_manufacturing', 0),
			'sourced_by_supplier': d.get('sourced_by_supplier', 0)
		}))

def get_exploded_items(self):
    """ Get all raw materials including items from child bom"""
    self.cur_exploded_items = {}
    for d in self.get('items'):
        this_doc = frappe.get_single("Manufacturing Settings")
        if hasattr(this_doc, 'disable_multi_level_bom'):
            if this_doc.disable_multi_level_bom is None:
                frappe.throw("Field disable_multi_level_bom does not exist on Manufacturing Settings")
            else:
                if this_doc.disable_multi_level_bom == 1:
                    self.add_to_cur_exploded_items(frappe._dict({
                        'item_code': d.item_code,
                        'item_name': d.item_name,
                        'operation': d.operation,
                        'source_warehouse': d.source_warehouse,
                        'description': d.description,
                        'image': d.image,
                        'main_item': self.item,
                        'stock_uom': d.stock_uom,
                        'stock_qty': flt(d.stock_qty),
                        'rate': flt(d.base_rate) / (flt(d.conversion_factor) or 1.0),
                        'include_item_in_manufacturing': d.include_item_in_manufacturing,
                        'sourced_by_supplier': d.sourced_by_supplier
                    }))
                else:
                    if d.bom_no:
                        self.get_child_exploded_items(d.bom_no, d.stock_qty)
                    else:
                        self.add_to_cur_exploded_items(frappe._dict({
                            'item_code': d.item_code,
                            'item_name': d.item_name,
                            'operation': d.operation,
                            'source_warehouse': d.source_warehouse,
                            'description': d.description,
                            'image': d.image,
                            'main_item': self.item,
                            'stock_uom': d.stock_uom,
                            'stock_qty': flt(d.stock_qty),
                            'rate': flt(d.base_rate) / (flt(d.conversion_factor) or 1.0),
                            'include_item_in_manufacturing': d.include_item_in_manufacturing,
                            'sourced_by_supplier': d.sourced_by_supplier
                        }))
        else:
            if d.bom_no:
                self.get_child_exploded_items(d.bom_no, d.stock_qty)
            else:
                self.add_to_cur_exploded_items(frappe._dict({
                    'item_code': d.item_code,
                    'item_name': d.item_name,
                    'operation': d.operation,
                    'source_warehouse': d.source_warehouse,
                    'description': d.description,
                    'image': d.image,
                    'main_item': self.item,
                    'stock_uom': d.stock_uom,
                    'stock_qty': flt(d.stock_qty),
                    'rate': flt(d.base_rate) / (flt(d.conversion_factor) or 1.0),
                    'include_item_in_manufacturing': d.include_item_in_manufacturing,
                    'sourced_by_supplier': d.sourced_by_supplier
                }))





BOM.get_child_exploded_items = get_child_exploded_items
BOM.get_exploded_items = get_exploded_items

# from erpnext.manufacturing.doctype.bom import bom as bom_file
# bom_file.get_bom_items_as_dict = get_bom_items_as_dict
