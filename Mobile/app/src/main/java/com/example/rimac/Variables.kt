package com.example.rimac

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class Variables : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.rimac)

        val activateGpsButton = findViewById<Button>(R.id.activateGpsButton)
        val randomLocationTextView = findViewById<TextView>(R.id.randomLocationTextView)
        val deactivateGpsButton = findViewById<Button>(R.id.deactivateGpsButton)

        // Configurar acciones para los botones
        activateGpsButton.setOnClickListener {
            // Aquí puedes agregar la lógica para activar el GPS y obtener la ubicación
            val randomLatitude = (Math.random() * 180 - 90).toFloat()
            val randomLongitude = (Math.random() * 360 - 180).toFloat()
            randomLocationTextView.text = getString(R.string.random_location, randomLatitude, randomLongitude)
        }

        deactivateGpsButton.setOnClickListener {
            // Aquí puedes agregar la lógica para desactivar el GPS
            randomLocationTextView.text = getString(R.string.gps_disabled)
        }
    }
}
