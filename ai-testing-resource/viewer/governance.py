"""Governance portal routes"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

governance = Blueprint('governance', __name__, url_prefix='/governance')

# Global repository instance (will be set by app initialization)
_repository = None


def init_governance(repository):
    """Initialize governance routes with repository

    Args:
        repository: TSRRepository instance
    """
    global _repository
    _repository = repository


@governance.route('/')
@governance.route('/dashboard')
def dashboard():
    """TSR list dashboard with filtering"""
    if not _repository:
        return "TSR repository not initialized", 500

    environment = request.args.get('environment')
    decision = request.args.get('decision')
    limit = int(request.args.get('limit', 50))

    tsrs = _repository.query(
        environment=environment,
        decision=decision,
        limit=limit
    )

    # Get statistics
    stats = {
        'total': _repository.count(),
        'go': _repository.count(decision='go'),
        'no_go': _repository.count(decision='no_go'),
        'pending_review': _repository.count(decision='pending_review'),
    }
    stats['go_rate'] = stats['go'] / stats['total'] if stats['total'] > 0 else 0

    return render_template(
        'governance/dashboard.html',
        tsrs=tsrs,
        stats=stats,
        active_nav='governance'
    )


@governance.route('/tsr/<tsr_id>')
def tsr_detail(tsr_id: str):
    """Detailed view of a single TSR"""
    if not _repository:
        return "TSR repository not initialized", 500

    tsr = _repository.get_by_id(tsr_id)
    if not tsr:
        return "TSR not found", 404

    return render_template(
        'governance/tsr_detail.html',
        tsr=tsr,
        active_nav='governance'
    )


@governance.route('/tsr/<tsr_id>/approve', methods=['POST'])
def approve_tsr(tsr_id: str):
    """Approve a TSR for deployment"""
    if not _repository:
        return "TSR repository not initialized", 500

    tsr = _repository.get_by_id(tsr_id)
    if not tsr:
        return "TSR not found", 404

    approved_by = request.form.get('approved_by')
    if not approved_by:
        flash('Approver name/email is required', 'error')
        return redirect(url_for('governance.tsr_detail', tsr_id=tsr_id))

    from tsr.models import GoNoGoDecision

    # Update approval status
    tsr.approved_by = approved_by
    tsr.approved_at = datetime.utcnow()

    # If pending review, change to GO
    if tsr.go_no_go_decision == GoNoGoDecision.PENDING_REVIEW:
        tsr.go_no_go_decision = GoNoGoDecision.GO
        tsr.decision_reason = f"Manually approved by {tsr.approved_by}"

    # Save updated TSR
    _repository.save(tsr)

    flash(f'TSR approved successfully by {approved_by}', 'success')
    return redirect(url_for('governance.tsr_detail', tsr_id=tsr_id))


@governance.route('/compare')
def compare_tsrs():
    """Compare two or more TSRs side-by-side"""
    if not _repository:
        return "TSR repository not initialized", 500

    tsr_ids = request.args.getlist('id')
    if len(tsr_ids) < 2:
        flash('Please select at least 2 TSRs to compare', 'error')
        return redirect(url_for('governance.dashboard'))

    tsrs = []
    for tsr_id in tsr_ids:
        tsr = _repository.get_by_id(tsr_id)
        if tsr:
            tsrs.append(tsr)

    if len(tsrs) < 2:
        flash('One or more TSRs not found', 'error')
        return redirect(url_for('governance.dashboard'))

    return render_template(
        'governance/comparison.html',
        tsrs=tsrs,
        active_nav='governance'
    )
