from fastapi import APIRouter, HTTPException

from rules.models import Rule, RuleCreate
from rules.storage import create_rule, delete_rule, get_rule, list_rules, update_rule

router = APIRouter(prefix="/api/rules", tags=["rules"])


@router.get("", response_model=list[Rule])
async def get_rules():
    return await list_rules()


@router.get("/{rule_id}", response_model=Rule)
async def get_rule_by_id(rule_id: str):
    rule = await get_rule(rule_id)
    if not rule:
        raise HTTPException(404, f"Rule '{rule_id}' not found")
    return rule


@router.post("", response_model=Rule, status_code=201)
async def add_rule(data: RuleCreate):
    return await create_rule(data)


@router.put("/{rule_id}", response_model=Rule)
async def modify_rule(rule_id: str, data: RuleCreate):
    rule = await update_rule(rule_id, data)
    if not rule:
        raise HTTPException(404, f"Rule '{rule_id}' not found")
    return rule


@router.delete("/{rule_id}", status_code=204)
async def remove_rule(rule_id: str):
    ok = await delete_rule(rule_id)
    if not ok:
        raise HTTPException(404, f"Rule '{rule_id}' not found")
