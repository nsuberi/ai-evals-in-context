"""REST API for TSR operations"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Optional

from .models import TestSummaryReport, GoNoGoDecision
from .repository import TSRRepository
from .rules import GoNoGoEvaluator

# Blueprint for TSR API
tsr_api = Blueprint('tsr_api', __name__)

# Global repository instance (will be set by app initialization)
_repository: Optional[TSRRepository] = None
_evaluator = GoNoGoEvaluator()


def init_tsr_api(repository: TSRRepository):
    """Initialize TSR API with repository

    Args:
        repository: TSRRepository instance
    """
    global _repository
    _repository = repository


@tsr_api.route('', methods=['POST'])
def create_tsr():
    """Create a new TSR

    Request body should contain TSR data in JSON format.

    Returns:
        JSON response with TSR ID and go/no-go decision
    """
    if not _repository:
        return jsonify({'error': 'TSR repository not initialized'}), 500

    try:
        data = request.get_json()
        tsr = TestSummaryReport.from_dict(data)

        # Apply go/no-go evaluation if not already set
        if tsr.go_no_go_decision == GoNoGoDecision.PENDING_REVIEW:
            _evaluator.apply_decision(tsr)

        # Save to database
        tsr_id = _repository.save(tsr)

        return jsonify({
            'id': tsr_id,
            'go_no_go_decision': tsr.go_no_go_decision.value,
            'decision_reason': tsr.decision_reason,
            'blocking_issues': tsr.blocking_issues,
            'warnings': tsr.warnings,
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@tsr_api.route('/<tsr_id>', methods=['GET'])
def get_tsr(tsr_id: str):
    """Get TSR by ID

    Args:
        tsr_id: TSR ID

    Returns:
        JSON response with full TSR data
    """
    if not _repository:
        return jsonify({'error': 'TSR repository not initialized'}), 500

    tsr = _repository.get_by_id(tsr_id)
    if not tsr:
        return jsonify({'error': 'TSR not found'}), 404

    return jsonify(tsr.to_dict())


@tsr_api.route('/latest', methods=['GET'])
def get_latest_tsr():
    """Get most recent TSR

    Query parameters:
        - environment: Filter by environment (optional)

    Returns:
        JSON response with TSR data
    """
    if not _repository:
        return jsonify({'error': 'TSR repository not initialized'}), 500

    environment = request.args.get('environment')
    tsr = _repository.get_latest(environment=environment)

    if not tsr:
        return jsonify({'error': 'No TSRs found'}), 404

    return jsonify(tsr.to_dict())


@tsr_api.route('/<tsr_id>/go-no-go', methods=['GET'])
def get_go_no_go(tsr_id: str):
    """Get go/no-go decision for a TSR

    This endpoint is designed for CI/CD pipelines to query deployment decisions.

    Args:
        tsr_id: TSR ID

    Returns:
        JSON response with decision data
    """
    if not _repository:
        return jsonify({'error': 'TSR repository not initialized'}), 500

    tsr = _repository.get_by_id(tsr_id)
    if not tsr:
        return jsonify({'error': 'TSR not found'}), 404

    return jsonify({
        'decision': tsr.go_no_go_decision.value,
        'reason': tsr.decision_reason,
        'blocking_issues': tsr.blocking_issues,
        'warnings': tsr.warnings,
        'manual_approval_required': tsr.manual_approval_required,
        'approved_by': tsr.approved_by,
        'approved_at': tsr.approved_at.isoformat() if tsr.approved_at else None,
    })


@tsr_api.route('/<tsr_id>/approve', methods=['POST'])
def approve_tsr(tsr_id: str):
    """Manually approve a TSR

    Request body:
        - approved_by: Name/email of approver (required)
        - notes: Optional approval notes

    Args:
        tsr_id: TSR ID

    Returns:
        JSON response with updated decision
    """
    if not _repository:
        return jsonify({'error': 'TSR repository not initialized'}), 500

    tsr = _repository.get_by_id(tsr_id)
    if not tsr:
        return jsonify({'error': 'TSR not found'}), 404

    data = request.get_json()
    if not data or 'approved_by' not in data:
        return jsonify({'error': 'approved_by is required'}), 400

    # Update approval status
    tsr.approved_by = data['approved_by']
    tsr.approved_at = datetime.utcnow()

    # If pending review, change to GO
    if tsr.go_no_go_decision == GoNoGoDecision.PENDING_REVIEW:
        tsr.go_no_go_decision = GoNoGoDecision.GO
        tsr.decision_reason = f"Manually approved by {tsr.approved_by}"

    # Save updated TSR
    _repository.save(tsr)

    return jsonify({
        'id': tsr.id,
        'decision': tsr.go_no_go_decision.value,
        'approved_by': tsr.approved_by,
        'approved_at': tsr.approved_at.isoformat(),
    })


@tsr_api.route('/query', methods=['GET'])
def query_tsrs():
    """Query TSRs with filters

    Query parameters:
        - environment: Filter by environment
        - decision: Filter by go/no-go decision
        - codebase_sha: Filter by codebase SHA
        - limit: Maximum results (default: 50)
        - offset: Pagination offset (default: 0)

    Returns:
        JSON response with list of TSRs
    """
    if not _repository:
        return jsonify({'error': 'TSR repository not initialized'}), 500

    environment = request.args.get('environment')
    decision = request.args.get('decision')
    codebase_sha = request.args.get('codebase_sha')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))

    tsrs = _repository.query(
        environment=environment,
        decision=decision,
        codebase_sha=codebase_sha,
        limit=limit,
        offset=offset
    )

    total = _repository.count(environment=environment, decision=decision)

    return jsonify({
        'tsrs': [tsr.to_dict() for tsr in tsrs],
        'total': total,
        'limit': limit,
        'offset': offset,
    })


@tsr_api.route('/<tsr_id>', methods=['DELETE'])
def delete_tsr(tsr_id: str):
    """Delete a TSR

    Args:
        tsr_id: TSR ID

    Returns:
        JSON response confirming deletion
    """
    if not _repository:
        return jsonify({'error': 'TSR repository not initialized'}), 500

    success = _repository.delete(tsr_id)
    if not success:
        return jsonify({'error': 'TSR not found'}), 404

    return jsonify({'message': 'TSR deleted successfully'})


@tsr_api.route('/stats', methods=['GET'])
def get_stats():
    """Get TSR statistics

    Query parameters:
        - environment: Filter by environment (optional)

    Returns:
        JSON response with statistics
    """
    # Get repository (fallback to Flask g object if global not set)
    repository = _repository
    if not repository:
        from flask import g
        if hasattr(g, 'tsr_repository'):
            repository = g.tsr_repository
        else:
            return jsonify({'error': 'TSR repository not initialized'}), 500

    environment = request.args.get('environment')

    total = repository.count(environment=environment)
    go_count = repository.count(environment=environment, decision='go')
    no_go_count = repository.count(environment=environment, decision='no_go')
    pending_count = repository.count(environment=environment, decision='pending_review')

    return jsonify({
        'total': total,
        'go': go_count,
        'no_go': no_go_count,
        'pending_review': pending_count,
        'go_rate': go_count / total if total > 0 else 0,
    })
