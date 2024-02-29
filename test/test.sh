  cpu_now=($(head -n1 /proc/stat)) 
  echo $cpu_now
  # Get all columns but skip the first (which is the "cpu" string) 
  cpu_sum="${cpu_now[@]:1}" 
  cpu_sum=$((${cpu_sum// /+})) 
  echo $cpu_sum 
