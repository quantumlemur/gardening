
node.startupcommand("@init.lua")
print("***** Starting ENTRY.  Setting startupcomand to INIT")

-----------------------  CONFIG  -----------------------

require("COMMON_DEFS")

print("ENTRY: Entry-only boot number "..rtcmem.read32(MEMSLOT_BOOTS_SINCE_INIT))
print("ENTRY: current voltage stored reading: "..rtcmem.read32(MEMSLOT_VOLTAGE))


rtcmem.write32(MEMSLOT_BOOTS_SINCE_INIT, rtcmem.read32(MEMSLOT_BOOTS_SINCE_INIT) + 1)


for i=21,32 do
	print("ENTRY: memslot "..i.." val: "..rtcmem.read32(i))
end
-----------------------  VOLTAGE  -----------------------


print("ENTRY: in main")


local voltage = adc.readvdd33()
local adcval = adc.read(0)
print("ENTRY: voltage reading: "..voltage)
print("ENTRY: adc reading: "..adcval)

if voltage ~= 65535 then
	adc.force_init_mode(adc.INIT_ADC)
else
	adc.force_init_mode(adc.INIT_VDD33)
end

-----------------------  MOVE ON TO NEXT STEP  -----------------------

require("exit")
