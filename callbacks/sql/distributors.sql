select dst.name, count(sc.*)
from distributors dst
join sim_cards sc on (sc.distributor_id=dst.id)
where (sc.channel_id > 0) and dst.is_active and (sc.direction=1)
group by dst.name
