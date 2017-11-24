select dst.name, dst.cut_code, dst.id, roma.range_a, roma.range_b
from routes_mask roma
join operators op on (op.id=roma.operator_id)
left join distributors dst on (dst.id=op.distributor_id)
join regions reg on (reg.id=roma.region_id)
where (aaa=%s and %s between range_a and range_b)
and dst.is_active and (dst.all_home or reg.is_home)
order by roma.timestamp desc
limit 1;
