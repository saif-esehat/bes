from odoo import http
from odoo.http import request
import json
import logging
import base64

_logger = logging.getLogger(__name__)

# CORS headers for API responses
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-CSRF-Token, Authorization',
    'Access-Control-Allow-Credentials': 'true'
}

class BatchesController(http.Controller):

    @http.route('/api/test', type='http', auth='none', methods=['GET'], csrf=False, cors='*')
    def api_test(self, **kwargs):
        """
        Simple test endpoint to verify the controller is working
        """
        return request.make_response(
            json.dumps({
                'success': True,
                'message': 'API test endpoint is working',
                'timestamp': '2024-11-01T09:55:00Z'
            }),
            headers={
                'Content-Type': 'application/json',
                **CORS_HEADERS
            }
        )
    """
    Controller for fetching dgs.batches data
    Provides API endpoints for React frontend to access batch information
    """

    @http.route('/api/batches', type='http', auth='user', methods=['GET', 'OPTIONS'], csrf=True, cors='*')
    def api_get_batches(self, **kwargs):
        """
        Fetch all dgs.batches in the specified format
        Returns JSON array of batch objects with required fields
        Only accessible to users with DGS Portal group
        """
        # Handle OPTIONS request for CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                '',
                headers=CORS_HEADERS,
                status=200
            )
        
        try:
            _logger.info("API: Fetching batches request received")
            _logger.info(f"API: Request method: {request.httprequest.method}")
            _logger.info(f"API: Request headers: {dict(request.httprequest.headers)}")
            _logger.info(f"API: Request URL: {request.httprequest.url}")
            
            # Check if user has DGS Portal group
            user = request.env.user
            if not user.has_group('bes.group_dgs_portal'):
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Access denied. User does not have DGS Portal permissions.'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=403
                )
            
            # Fetch all dgs.batches records with proper access controls
            batches = request.env['dgs.batches'].search([('documents_uploaded','=',True)], order='create_date desc')
            _logger.info(f"API: Found {len(batches)} batches")
            
            # Debug: Check if model exists and is accessible
            if not batches:
                _logger.info("API: No batches found in database")
            
            # Transform data to match the required format
            exam_batches = []
            
            for batch in batches:
                # Map batch state to the required status format
                status_mapping = {
                    'pending': 'approval_pending',
                    'approved': 'approved'
                }
                
                # Determine exam type based on batch name or other criteria
                exam_type = 'Repeater' if batch.repeater_batch else 'Regular'
                
                # Create batch object in required format
                batch_data = {
                    'id': f'BATCH{batch.id:03d}',
                    'name': batch.batch_name or 'Unnamed Batch',
                    'from_date': batch.from_date.strftime('%Y-%m-%d') if batch.from_date else '2024-11-15',
                    'to_date': batch.to_date.strftime('%Y-%m-%d') if batch.to_date else '2024-11-15',
                    'status': status_mapping.get(batch.dgs_approval_state, 'approval_pending'),
                    'examType': exam_type,
                    'documents': [
                        {
                            'id': doc.id,
                            'name': doc.name,
                            'uploadDate': doc.upload_date.strftime('%Y-%m-%d') if doc.upload_date else '2024-11-15'
                        }
                        for doc in batch.document_ids
                    ]
                }
                exam_batches.append(batch_data)
            
            _logger.info(f"API: Returning {len(exam_batches)} batches")
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'data': exam_batches
                }),
                headers={
                    'Content-Type': 'application/json',
                    **CORS_HEADERS
                }
            )
            
        except Exception as e:
            
            print(e)
            _logger.error(f"Error fetching batches: {str(e)}")
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': f'Failed to fetch batches: {str(e)}'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )

    @http.route('/api/batches/<int:batch_id>', type='http', auth='user', methods=['GET', 'OPTIONS'], csrf=True, cors='*')
    def api_get_batch_detail(self, batch_id, **kwargs):
        """
        Fetch specific dgs.batch by ID
        Returns detailed batch information
        Only accessible to users with DGS Portal group
        """
        # Handle OPTIONS request for CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                '',
                headers=CORS_HEADERS,
                status=200
            )
        
        try:
            # Check if user has DGS Portal group
            user = request.env.user
            if not user.has_group('bes.group_dgs_portal'):
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Access denied. User does not have DGS Portal permissions.'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=403
                )

            # Fetch specific batch with proper access controls
            batch = request.env['dgs.batches'].browse(batch_id)
            
            if not batch.exists():
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Batch not found'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=404
                )
            
            # Map batch state to the required status format
            status_mapping = {
                '1-on_going': 'approval_pending',
                '2-confirmed': 'approved', 
                '3-dgs_approved': 'approved'
            }
            
            # Determine exam type based on batch name or other criteria
            exam_type = 'Repeater' if batch.repeater_batch else 'Regular'
            
            # Create detailed batch object
            batch_data = {
                'id': f'BATCH{batch.id:03d}',
                'name': batch.batch_name or 'Unnamed Batch',
                'from_date': batch.from_date.strftime('%Y-%m-%d') if batch.from_date else '2024-11-15',
                'to_date': batch.to_date.strftime('%Y-%m-%d') if batch.to_date else '2024-11-15',
                'status': status_mapping.get(batch.state, 'approval_pending'),
                'examType': exam_type,
                'documents': [
                    {
                        'id': doc.id,
                        'name': doc.name,
                        'uploadDate': doc.upload_date.strftime('%Y-%m-%d') if doc.upload_date else '2024-11-15'
                    }
                    for doc in batch.document_ids
                ],
                'additional_info': {
                    'is_current_batch': batch.is_current_batch,
                    'repeater_batch': batch.repeater_batch,
                    'dgs_approval_state': batch.dgs_approval_state,
                    'report_status': batch.report_status
                }
            }
            
            _logger.info(f"Fetched batch {batch_id} for DGS Portal")
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'data': batch_data
                }),
                headers={
                    'Content-Type': 'application/json',
                    **CORS_HEADERS
                }
            )
            
        except Exception as e:
            _logger.error(f"Error fetching batch {batch_id}: {str(e)}")
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': f'Failed to fetch batch: {str(e)}'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )

    @http.route('/api/batches/<int:batch_id>/documents/<int:document_id>/download', type='http', auth='user', methods=['GET', 'OPTIONS'], csrf=True, cors='*')
    def api_download_batch_document(self, batch_id, document_id, **kwargs):
        """
        Download a specific document from a batch
        Returns the document file as a downloadable response
        Only accessible to users with DGS Portal group
        """
        # Handle OPTIONS request for CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                '',
                headers=CORS_HEADERS,
                status=200
            )
        
        try:
            _logger.info(f"API: Download document request received - batch_id: {batch_id}, document_id: {document_id}")
            
            # Check if user has DGS Portal group
            user = request.env.user
            if not user.has_group('bes.group_dgs_portal'):
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Access denied. User does not have DGS Portal permissions.'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=403
                )

            # Fetch the batch to verify access
            batch = request.env['dgs.batches'].browse(batch_id)
            
            if not batch.exists():
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Batch not found'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=404
                )
            
            # Fetch the specific document
            document = request.env['batch.document'].browse(document_id)
            
            if not document.exists():
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Document not found'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=404
                )
            
            # Verify the document belongs to the specified batch
            if document.dgs_batch_id.id != batch_id:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Document does not belong to the specified batch'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=400
                )
            
            # Check if document has file data
            if not document.document_file:
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Document file not available'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=404
                )
            
            # Get filename - use document_filename if available, otherwise use name with .pdf extension
            filename = document.document_filename or f"{document.name}.pdf"
            
            # Decode base64 content
            try:
                file_content = base64.b64decode(document.document_file)
            except Exception as decode_error:
                _logger.error(f"Error decoding base64 content for document {document_id}: {str(decode_error)}")
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Invalid document file format'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=500
                )
            
            _logger.info(f"API: Downloading document '{filename}' from batch {batch_id}")
            
            # Return the file as downloadable response
            return request.make_response(
                file_content,
                headers={
                    'Content-Type': 'application/octet-stream',
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    **CORS_HEADERS
                }
            )
            
        except Exception as e:
            _logger.error(f"Error downloading document {document_id} from batch {batch_id}: {str(e)}")
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': f'Failed to download document: {str(e)}'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )

    @http.route('/api/batches/<int:batch_id>/approve', type='http', auth='user', methods=['POST', 'OPTIONS'], csrf=False, cors='*')
    def api_approve_batch(self, batch_id, **kwargs):
        """
        Approve a specific dgs.batch by ID
        Sets dgs_approval_state to 'approved'
        Only accessible to users with DGS Portal group and proper permissions
        """
        # Handle OPTIONS request for CORS preflight
        if request.httprequest.method == 'OPTIONS':
            return request.make_response(
                '',
                headers=CORS_HEADERS,
                status=200
            )
        
        try:
            _logger.info(f"API: Approve batch request received - batch_id: {batch_id}")
            
            # Check if user has DGS Portal group
            user = request.env.user
            if not user.has_group('bes.group_dgs_portal'):
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Access denied. User does not have DGS Portal permissions.'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=403
                )

            # Fetch the specific batch
            batch = request.env['dgs.batches'].browse(batch_id)
            
            if not batch.exists():
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Batch not found'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=404
                )
            
            # Check if batch is already approved
            if batch.dgs_approval_state == 'approved':
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Batch is already approved'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=400
                )
            
            # Check if batch is in correct state for approval
            if batch.state != '2-confirmed':
                return request.make_response(
                    json.dumps({
                        'success': False,
                        'error': 'Batch must be in confirmed state before DGS approval'
                    }),
                    headers={'Content-Type': 'application/json'},
                    status=400
                )
            
            # Approve the batch
            batch.dgs_approved()
            
            _logger.info(f"API: Successfully approved batch {batch_id}")
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'message': f'Batch {batch.batch_name} has been approved successfully',
                    'data': {
                        'id': batch.id,
                        'name': batch.batch_name,
                        'dgs_approval_state': batch.dgs_approval_state,
                        'status': 'approved'
                    }
                }),
                headers={
                    'Content-Type': 'application/json',
                    **CORS_HEADERS
                }
            )
            
        except Exception as e:
            _logger.error(f"Error approving batch {batch_id}: {str(e)}")
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': f'Failed to approve batch: {str(e)}'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )