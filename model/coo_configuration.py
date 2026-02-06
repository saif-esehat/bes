from odoo import models, fields, api


class COOConfiguration(models.Model):
    _name = 'bes.coo.configuration'
    _description = 'COO/CEO Configuration'
    _order = 'cutoff_date desc'
    
    # COO Fields
    coo_name = fields.Char(string='COO Name', required=True, default='')
    coo_designation = fields.Char(string='COO Designation', required=True, default='')
    coo_signature_image = fields.Binary(string='COO Signature Image', attachment=True)
    
    # CEO Fields
    ceo_name = fields.Char(string='CEO Name', required=True, default='')
    ceo_designation = fields.Char(string='CEO Designation', required=True, default='')
    ceo_signature_image = fields.Binary(string='CEO Signature Image', attachment=True)
    
    cutoff_date = fields.Date(string='Cutoff Date', required=True, default='')
    active = fields.Boolean(string='Active', default=True)
    
    @api.model
    def get_current_config(self, batch_date=None, officer_type='coo'):
        """
        Get the appropriate configuration based on batch date and officer type.
        If batch_date is provided and is before a cutoff date, return the configuration
        that was active at that time.
        If batch_date is after cutoff date or not provided, return the latest active configuration.
        
        :param batch_date: Date to check against cutoff dates
        :param officer_type: 'coo' or 'ceo' - which officer configuration to return
        :return: Dictionary with name, designation, signature_image, and signature_image_url
        """
        configs = self.search([('active', '=', True)], order='cutoff_date desc')
        
        # import wdb;wdb.set_trace();
        if not configs:
            # Return default values if no configuration exists
            return self._get_default_config(officer_type)
        
        if batch_date:
            # Find the configuration where cutoff_date <= batch_date
            for config in configs:
                if config.cutoff_date and batch_date >= config.cutoff_date:
                    return self._config_to_dict(config, officer_type)
            # If batch_date is before all cutoff dates, return the oldest configuration
            return self._config_to_dict(configs[-1], officer_type)
        else:
            # No batch date provided, return the latest configuration
            return self._config_to_dict(configs[0], officer_type)
    
    def _get_default_config(self, officer_type):
        """Return default configuration based on officer type."""
        if officer_type == 'ceo':
            return {
                'name': 'Ravindra Nath Tripathi',
                'designation': 'Chief Executive Officer',
                'signature_image': '',
                'signature_image_url': '/bes/static/src/img/Ravindra_Nath_tripathi-NoBg_Sign.png'
            }
        else:  # coo
            return {
                'name': 'Ravindra Nath Tripathi',
                'designation': 'Marine Engineering Officer',
                'signature_image': '',
                'signature_image_url': '/bes/static/src/img/Ravindra_Nath_tripathi-NoBg_Sign.png'
            }
    
    def _config_to_dict(self, config, officer_type):
        """Convert config record to dictionary for template use."""
        if officer_type == 'ceo':
            signature_image = config.ceo_signature_image
            # Ensure signature_image is a string (base64) not bytes
            if signature_image and isinstance(signature_image, bytes):
                signature_image = signature_image.decode('utf-8')
            return {
                'name': config.ceo_name,
                'designation': config.ceo_designation,
                'signature_image': signature_image,
                'signature_image_url': f'/web/image/bes.coo.configuration/{config.id}/ceo_signature_image' if signature_image else '/bes/static/src/img/Ravindra_Nath_tripathi-NoBg_Sign.png'
            }
        else:  # coo
            signature_image = config.coo_signature_image
            # Ensure signature_image is a string (base64) not bytes
            if signature_image and isinstance(signature_image, bytes):
                signature_image = signature_image.decode('utf-8')
            return {
                'name': config.coo_name,
                'designation': config.coo_designation,
                'signature_image': signature_image,
                'signature_image_url': f'/web/image/bes.coo.configuration/{config.id}/coo_signature_image' if signature_image else '/bes/static/src/img/Ravindra_Nath_tripathi-NoBg_Sign.png'
            }