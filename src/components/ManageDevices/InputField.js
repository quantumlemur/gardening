import React from "react";

import "gestalt/dist/gestalt.css";
import { Box, TextField } from "gestalt";

function InputField({
  name,
  value,
  placeholder,
  type,
  disabled,
  label,
  date,
  helperText,
  onChange,
  errorMessage,
}) {
  if (type === "datetime-local") {
    type = "text";
    value = String(new Date(value * 1000));
  } else {
    value = String(value);
  }
  return (
    <Box flex="grow" padding={3}>
      <TextField
        key={name}
        id={name}
        label={label ? label : name}
        name={name}
        value={value}
        helperText={helperText}
        onChange={(e) => onChange(e.event)}
        placeholder={placeholder ? placeholder : name}
        disabled={disabled}
        errorMessage={errorMessage}
        type={type}
      />
    </Box>
  );
}

export default InputField;
