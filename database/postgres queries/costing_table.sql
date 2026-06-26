create table costing(
	date_of_modify TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
	monthly_plan int,
	yearly_plan int,
	cost_per_inovice int,
	one_time_payment int
	
)