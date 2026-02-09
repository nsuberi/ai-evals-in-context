"""Governance portal routes"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime

governance = Blueprint("governance", __name__)

# Global repository instance (will be set by app initialization)
_repository = None


def init_governance(repository):
    """Initialize governance routes with repository

    Args:
        repository: TSRRepository instance
    """
    global _repository
    _repository = repository


@governance.route("/")
@governance.route("/dashboard")
def index():
    """Redirect to TSR Evidence page (narrative governance)"""
    return redirect(url_for("narrative.governance"))


@governance.route("/tsr/<tsr_id>")
def tsr_detail(tsr_id: str):
    """Detailed view of a single TSR"""
    if not _repository:
        return "TSR repository not initialized", 500

    tsr = _repository.get_by_id(tsr_id)
    if not tsr:
        return "TSR not found", 404

    return render_template(
        "governance/tsr_detail.html", tsr=tsr, active_nav="governance"
    )


@governance.route("/tsr/<tsr_id>/detail-fragment")
def tsr_detail_fragment(tsr_id: str):
    """Return TSR detail as an HTML fragment for modal injection"""
    if not _repository:
        return "TSR repository not initialized", 500

    tsr = _repository.get_by_id(tsr_id)
    if not tsr:
        return "TSR not found", 404

    return render_template(
        "governance/_tsr_modal_content.html",
        tsr=tsr,
    )


@governance.route("/tsr/<tsr_id>/download")
def tsr_download(tsr_id: str):
    """Download TSR as JSON file"""
    if not _repository:
        return "TSR repository not initialized", 500

    tsr = _repository.get_by_id(tsr_id)
    if not tsr:
        return "TSR not found", 404

    response = jsonify(tsr.to_dict())
    decision = tsr.go_no_go_decision.value
    filename = f"tsr-{tsr_id[:8]}-{decision}.json"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


@governance.route("/tsr/<tsr_id>/approve", methods=["POST"])
def approve_tsr(tsr_id: str):
    """Approve a TSR for deployment"""
    if not _repository:
        return "TSR repository not initialized", 500

    tsr = _repository.get_by_id(tsr_id)
    if not tsr:
        return "TSR not found", 404

    approved_by = request.form.get("approved_by")
    if not approved_by:
        flash("Approver name/email is required", "error")
        return redirect(url_for("governance.tsr_detail", tsr_id=tsr_id))

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

    flash(f"TSR approved successfully by {approved_by}", "success")
    return redirect(url_for("governance.tsr_detail", tsr_id=tsr_id))


@governance.route("/compare")
def compare_tsrs():
    """Compare two or more TSRs side-by-side"""
    if not _repository:
        return "TSR repository not initialized", 500

    tsr_ids = request.args.getlist("id")
    if len(tsr_ids) < 2:
        flash("Please select at least 2 TSRs to compare", "error")
        return redirect(url_for("governance.dashboard"))

    tsrs = []
    for tsr_id in tsr_ids:
        tsr = _repository.get_by_id(tsr_id)
        if tsr:
            tsrs.append(tsr)

    if len(tsrs) < 2:
        flash("One or more TSRs not found", "error")
        return redirect(url_for("governance.dashboard"))

    return render_template(
        "governance/comparison.html", tsrs=tsrs, active_nav="governance"
    )
