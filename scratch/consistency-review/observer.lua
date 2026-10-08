if player(1) and roundState() == 2 then
 local t=var(58)
 if t~=lastPreview then
  lastPreview=t
  if t==1530 or t==1550 or t==1570 or t==1590 or t==1610 or t==1630 or t==1670 or t==1720 then screenshot() end
  if t>=1800 then os.exit() end
 end
end
