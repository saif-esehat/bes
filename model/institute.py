from odoo import api, fields, models
from odoo.exceptions import UserError,ValidationError
from datetime import datetime
import random
import string



class Institute(models.Model):
    _name = "bes.institute"
    _description= 'Course Master'
    _rec_name = 'name'

    code = fields.Char("Code")
    name = fields.Char("Name")
    email = fields.Char("Email")
    state = fields.Many2one("res.country.state","State",domain=[('country_id.code','=','IN')])
    mti = fields.Char("MTI no.")
    courses = fields.One2many("institute.courses","institute_id","Courses")
    user_id = fields.Many2one("res.users", "Portal User")
    exam_center = fields.Many2one("exam.center", "Exam Center")
    street = fields.Char("Street")
    street2 = fields.Char("Street2")
    city = fields.Char("City",required=True)
    zip = fields.Char("Zip",required=True)
    
    principal_name = fields.Char("Name of Principal / Trustee of Training Institute")
    principal_phone = fields.Char("Phone No. of Principal / Trustee of Training Institute")
    principal_mobile = fields.Char("Mobile No. of Principal / Trustee of Training Institute")
    principal_email= fields.Char("E-mail of Principal / Trustee of Training Institute")
    
    
    admin_phone = fields.Char("Phone No. of Admin Officer of Training Institute")
    admin_mobile = fields.Char("Mobile No. of Admin Officer of Training Institute")
    admin_email= fields.Char("E-mail of Admin Officer of Training Institute")
    
    name_of_second_authorized_person = fields.Char("Name of the second authorised person representing the Institute")
    
    institute_computer_lab = fields.Boolean("Does the institue have inhouse Computer Lab")
    computer_lab_pc_count = fields.Integer("How many PC does the computer Lab Have")
    internet_strength = fields.Char("Strength of Internet connection")
    institute_approved_conduct_stcw = fields.Boolean("Is the Institute Approved to conduct STCW and Security Courses")
    is_lab_used_for_stcw_exit_exam = fields.Boolean("IS the Lab being used for STCW exit exams")
    

    def open_create_institute_batches_wizard(self):
        # Create a new instance of the wizard
        wizard = self.env['create.institute.batches.wizard'].create({
            'batch_name': '',  # Set default values if needed
        })

        # Open the wizard view
        return {
            'name': 'Create Institute Batches',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.institute.batches.wizard',
            'res_id': wizard.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context,  # Pass the current context
        }

    def _generate_password(self, length=8):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))
    

    @api.model
    def create(self, values):
        institute = super(Institute, self).create(values)
        user_values = {
            'name': institute.name,
            'login': institute.email,  # You can set the login as the same as the user name
            'password': 12345678,  # Generate a random password
            'sel_groups_1_9_10':9
        }
 
        portal_user = self.env['res.users'].sudo().create(user_values)
        institute.write({'user_id': portal_user.id})  # Associate the user with the institute
        # import wdb; wdb.set_trace()
        institute_tag = self.env.ref('bes.institute_tag').id
        portal_user.partner_id.write({'email': institute.email,'state_id':institute.state.id,'category_id':[institute_tag]})
        
        principal_contact_values = {
            'type':'contact',
            'name': institute.principal_name,
            'phone': institute.principal_phone,
            'mobile': institute.principal_mobile,
            'email': institute.principal_email,
            'function': 'Principal'
        }
        
        
        contact_partner = self.env['res.partner'].create(principal_contact_values)
    
        # Link the contact partner with the user's partner
        portal_user.partner_id.write({'child_ids': [(4, contact_partner.id)]})
        
        
        # Create a contact under the partner_id
        admin_contact_values = {
            'type':'contact',
            'name': institute.name_of_second_authorized_person,
            'phone': institute.admin_phone,
            'mobile': institute.admin_mobile,
            'email': institute.admin_email,
            'function': 'Office Administrator'
        }
        
        
        contact_partner = self.env['res.partner'].create(admin_contact_values)
    
        # Link the contact partner with the user's partner
        portal_user.partner_id.write({'child_ids': [(4, contact_partner.id)]})
        
        
        

        
        return institute
    
    
    def batch_button(self):
        
        return {
        'name': 'Batch',
        'domain': [('institute_id', '=', self.id)],
        'view_type': 'form',
        'res_model': 'institute.batches',
        'view_id': False,
        'view_mode': 'tree,form',
        'type': 'ir.actions.act_window',
        'context': {
            'default_institute_id': self.id    
            }
        }



    


class InstituteCourses(models.Model):
    _name = "institute.courses"
    _description= 'Institute Courses'
    _sql_constraints = [
        ('unique_course_per_institute', 'unique(institute_id, course)', 'Course must be unique per institute.'),
    ]
    institute_id = fields.Many2one("bes.institute","Institute ID")
    course = fields.Many2one("course.master","Course")
    approved_capacity = fields.Integer("Approved Capacity")
    approved_date = fields.Date("Approved Date")


